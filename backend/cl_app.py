import chainlit as cl
from langchain_aws import ChatBedrockConverse
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from typing import cast
from langchain.schema.runnable import RunnableConfig, Runnable
from chainlit import Message
import boto3
from botocore.exceptions import ClientError
import random
from spellchecker import SpellChecker  # Utilisation de pyspellchecker
from langdetect import detect  # Pour la détection de la langue
from dotenv import load_dotenv

load_dotenv()

# Initialiser le correcteur orthographique pour le français
spell = SpellChecker(language="fr")

# Fonction pour calculer le pourcentage de fautes d'orthographe
def calculer_fautes(message):
    mots = message.split()
    mots_incorrects = spell.unknown(mots)
    pourcentage_fautes = (len(mots_incorrects) / len(mots)) * 100 if mots else 0
    return pourcentage_fautes

# Fonction pour ajouter des lettres aléatoires dans un mot
def deform_word(word):
    if len(word) > 3:  # Pour éviter de trop déformer les petits mots
        pos = random.randint(1, len(word) - 2)
        letter = chr(random.randint(97, 122))  # Lettre aléatoire
        return word[:pos] + letter + word[pos:]
    return word

# Fonction pour déformer la réponse si le nombre de fautes est élevé
def deform_response(response):
    words = response.split()
    return " ".join(deform_word(word) for word in words)

@cl.on_chat_start
async def on_chat_start():
    await Message(
        content="Bonjour ! Souhaitez-vous utiliser le chatbot en version **généraliste** ou en version experte en **EHS** ?\n\nVeuillez répondre par 'généraliste' ou 'ehs'."
    ).send()

@cl.on_message
async def on_message(message: Message):
    # Vérifier si le mode est déjà stocké dans la session
    mode = cl.user_session.get("mode")

    if not mode:
        mode_input = message.content.strip().lower()

        if mode_input in ["généraliste", "ehs"]:
            mode = mode_input
        else:
            client = boto3.client("bedrock-runtime", region_name="us-west-2")
            model_id = "anthropic.claude-3-haiku-20240307-v1:0"
            user_message = f"""Vous agirez en tant qu'assistant IA. Votre objectif est de déterminer si l'utilisateur souhaite utiliser le chatbot en mode généraliste ou en mode expert en EHS (Environnement, Hygiène et Sécurité).

Voici les règles importantes pour l'interaction :
- Si vous êtes sûr que l'utilisateur veut le mode généraliste, répondez uniquement par "généraliste".
- Si vous êtes sûr que l'utilisateur veut le mode EHS, répondez uniquement par "ehs".
- Si vous êtes sûr que l'utilisateur dit précisement 'mode alcoolique' répondez alcool
- Si vous n'êtes pas sûr ou si vous ne comprenez pas, répondez uniquement par "inconnu".

Voici la question de l'utilisateur : {message.content}"""

            conversation = [{"role": "user", "content": [{"text": user_message}]}]

            try:
                response = client.converse(
                    modelId=model_id,
                    messages=conversation,
                    inferenceConfig={"maxTokens": 200, "temperature": 0},
                )
                response_text = response["output"]["message"]["content"][0]["text"].strip().lower()
                print(f"Réponse du modèle Haiku : {response_text}")

            except (ClientError, Exception) as e:
                print(f"ERREUR : Impossible d'invoquer '{model_id}'. Raison : {e}")
                await Message(content="Une erreur est survenue lors de la communication avec le modèle. Veuillez réessayer plus tard.").send()
                return

            if response_text in ["généraliste", "ehs", "alcool"]:
                mode = response_text
            else:
                mode = "inconnu"

        if mode == "inconnu":
            await Message(content="Je n'ai pas compris votre choix. Veuillez me redonner votre réponse en précisant 'généraliste' ou 'ehs'.").send()
            return

        cl.user_session.set("mode", mode)

        llm = ChatBedrockConverse(
            model="anthropic.claude-3-sonnet-20240229-v1:0",
            region_name="us-west-2",
            temperature=0,
            max_tokens=None
        )

        if mode == "généraliste":
            prompt = ChatPromptTemplate.from_messages(
                [("system", "Vous êtes un assistant généraliste dont la tâche est de répondre à des questions générales. Commençons !"),
                 ("human", "{question}")]
            )
        elif mode == "ehs":
            prompt = ChatPromptTemplate.from_messages(
                [("system", "Vous êtes un expert en EHS (Environnement, Hygiène et Sécurité) et votre tâche est de répondre aux questions liées à ce domaine. Avec votre expertise, vous pouvez aider les gens à mieux comprendre l'EHS. Commençons !"),
                 ("human", "{question}")]
            )
        elif mode == "alcool":
            prompt = ChatPromptTemplate.from_messages(
                [("system", "Tu es un assistant généraliste mais toute tes réponses doivent posséder leur lettre dans le désordre, tu dois donc générer ta réponse puis mettre les lettres a des positions aléatoire !"),
                 ("human", "{question}")]
            )

        runnable = prompt | llm | StrOutputParser()
        cl.user_session.set("runnable", runnable)
        await Message(content=f"Le chatbot est prêt à être utilisé en mode **{mode}**. Posez vos questions !").send()
        return

    else:
        runnable = cast(Runnable, cl.user_session.get("runnable"))

    if runnable is None:
        await Message(content="Erreur : Le chatbot n'a pas été correctement configuré. Veuillez redémarrer et choisir un mode.").send()
        return

    # Vérifier la langue du message et calculer les fautes si c'est en français
    langue = detect(message.content)
    pourcentage_fautes = 0
    if langue == "fr":
        pourcentage_fautes = calculer_fautes(message.content)

    msg = Message(content="")

    async for chunk in runnable.astream(
        {"question": message.content},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        response_chunk = chunk
        # Appliquer la déformation uniquement si le texte est en français et que le seuil de fautes est dépassé
        if langue == "fr" and pourcentage_fautes > 50:
            response_chunk = deform_response(response_chunk)
        
        await msg.stream_token(response_chunk)

    await msg.send()
