import chainlit as cl
from langchain_aws import ChatBedrockConverse
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from typing import cast
from langchain.schema.runnable import RunnableConfig, Runnable
from chainlit import Message
import boto3
from botocore.exceptions import ClientError

from dotenv import load_dotenv

load_dotenv()

@cl.on_chat_start
async def on_chat_start():
    # Au démarrage, le chatbot demande à l'utilisateur de choisir le mode
    await Message(
        content="Bonjour ! Souhaitez-vous utiliser le chatbot en version **généraliste** ou en version experte en **EHS** ?\n\nVeuillez répondre par 'généraliste' ou 'ehs'."
    ).send()

@cl.on_message
async def on_message(message: Message):

    # Vérifier si le mode est déjà stocké dans la session
    mode = cl.user_session.get("mode")

    if not mode:
        # Si le mode n'est pas défini, on doit le déterminer
        mode_input = message.content.strip().lower()

        if mode_input in ["généraliste", "ehs"]:
            mode = mode_input
        else:
            # Utiliser le modèle Haiku pour déterminer le mode

            # Créer un client Bedrock Runtime
            client = boto3.client("bedrock-runtime", region_name="us-west-2")

            # ID du modèle
            model_id = "anthropic.claude-3-haiku-20240307-v1:0"

            # Préparer le prompt pour le modèle
            user_message = f"""Vous agirez en tant qu'assistant IA. Votre objectif est de déterminer si l'utilisateur souhaite utiliser le chatbot en mode généraliste ou en mode expert en EHS (Environnement, Hygiène et Sécurité).

Voici les règles importantes pour l'interaction :
- Si vous êtes sûr que l'utilisateur veut le mode généraliste, répondez uniquement par "généraliste".
- Si vous êtes sûr que l'utilisateur veut le mode EHS, répondez uniquement par "ehs".
- Si vous n'êtes pas sûr ou si vous ne comprenez pas, répondez uniquement par "inconnu".

Voici la question de l'utilisateur : {message.content}"""

            conversation = [
                {
                    "role": "user",
                    "content": [{"text": user_message}],
                }
            ]

            try:
                # Envoyer le message au modèle
                response = client.converse(
                    modelId=model_id,
                    messages=conversation,
                    inferenceConfig={"maxTokens": 10, "temperature": 0},
                )

                # Extraire la réponse
                response_text = response["output"]["message"]["content"][0]["text"].strip().lower()
                print(f"Réponse du modèle Haiku : {response_text}")

            except (ClientError, Exception) as e:
                print(f"ERREUR : Impossible d'invoquer '{model_id}'. Raison : {e}")
                await Message(content="Une erreur est survenue lors de la communication avec le modèle. Veuillez réessayer plus tard.").send()
                return

            if response_text in ["généraliste", "ehs"]:
                mode = response_text
            else:
                mode = "inconnu"

        if mode == "inconnu":
            await Message(content="Je n'ai pas compris votre choix. Veuillez me redonner votre réponse en précisant 'généraliste' ou 'ehs'.").send()
            return

        # Stocker le mode dans la session utilisateur
        cl.user_session.set("mode", mode)

        # Initialiser le modèle en fonction du mode choisi
        llm = ChatBedrockConverse(
            model="anthropic.claude-3-sonnet-20240229-v1:0",
            region_name="us-west-2",
            temperature=0,
            max_tokens=None
        )

        if mode == "généraliste":
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", "Vous êtes un assistant généraliste dont la tâche est de répondre à des questions générales. Commençons !"),
                    ("human", "{question}"),
                ]
            )
        elif mode == "ehs":
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", "Vous êtes un expert en EHS (Environnement, Hygiène et Sécurité) et votre tâche est de répondre aux questions liées à ce domaine. Avec votre expertise, vous pouvez aider les gens à mieux comprendre l'EHS. Commençons !"),
                    ("human", "{question}"),
                ]
            )

        runnable = prompt | llm | StrOutputParser()
        cl.user_session.set("runnable", runnable)

        await Message(content=f"Le chatbot est prêt à être utilisé en mode **{mode}**. Posez votre question !").send()
        return  # L'utilisateur peut maintenant envoyer des messages

    else:
        # Si le mode est déjà défini, récupérer le runnable
        runnable = cast(Runnable, cl.user_session.get("runnable"))

        if runnable is None:
            await Message(content="Erreur : Le chatbot n'a pas été correctement configuré. Veuillez redémarrer et choisir un mode.").send()
            return

        # Traiter le message de l'utilisateur
        msg = Message(content="")
        
        async for chunk in runnable.astream(
            {"question": message.content},
            config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
        ):
            await msg.stream_token(chunk)

        await msg.send()
