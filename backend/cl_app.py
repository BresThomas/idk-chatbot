import chainlit as cl
from langchain_aws import ChatBedrockConverse
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from typing import cast
from langchain.schema.runnable import RunnableConfig, Runnable
from chainlit import Image, Message
import boto3
from botocore.exceptions import ClientError
import random
from spellchecker import SpellChecker
from langdetect import detect  # Pour la détection de la langue
from dotenv import load_dotenv
from io import BytesIO
import json  # Pour traiter la réponse JSON
import base64  # Pour décoder l'image en base64

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
        content="Bonjour ! Souhaitez-vous utiliser le chatbot en version **généraliste**, **EHS**, ou pour générer une **image** ?\n\n."
    ).send()

@cl.on_message
async def on_message(message: Message):
    # Initialiser le client Bedrock pour toutes les opérations
    client = boto3.client("bedrock-runtime", region_name="us-west-2")

    # Vérifier si le mode est déjà stocké dans la session
    mode = cl.user_session.get("mode")

    if not mode:
        mode_input = message.content.strip().lower()

        if mode_input in ["généraliste", "ehs", "image", "alcool"]:
            mode = mode_input
        else:
            model_id = "anthropic.claude-3-haiku-20240307-v1:0"
            user_message = f"""Vous agirez en tant qu'assistant IA. Votre objectif est de déterminer si l'utilisateur souhaite utiliser le chatbot en mode généraliste, en mode expert en EHS (Environnement, Hygiène et Sécurité), pour générer une image, ou en mode alcoolique.

Voici les règles importantes pour l'interaction :
- Si vous êtes sûr que l'utilisateur veut le mode généraliste, répondez uniquement par "généraliste".
- Si vous êtes sûr que l'utilisateur veut le mode EHS, répondez uniquement par "ehs".
- Si vous êtes sûr que l'utilisateur veut générer une image, une photo, un dessin, répondez uniquement par "image".
- Si vous êtes sûr que l'utilisateur dit précisément 'mode alcoolique', répondez "alcool".
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

            if response_text in ["généraliste", "ehs", "alcool", "image"]:
                mode = response_text
            else:
                mode = "inconnu"

        if mode == "inconnu":
            await Message(content="Je n'ai pas compris votre choix. Veuillez me redonner votre réponse en précisant 'généraliste', 'ehs', ou 'image'.").send()
            return

        cl.user_session.set("mode", mode)

        if mode == "image":
            # Pour le mode image, on n'utilise pas un LLM, mais on stocke simplement le mode
            await Message(content=f"Le chatbot est prêt à générer des images. Décrivez l'image que vous souhaitez obtenir !").send()
            return

        else:
            # Initialiser le LLM pour les autres modes
            llm = ChatBedrockConverse(
                model="anthropic.claude-3-sonnet-20240229-v1:0",
                region_name="us-west-2",
                temperature=0,
                max_tokens=None
            )

            if mode == "généraliste":
                prompt = ChatPromptTemplate.from_messages(
                    [("system", "Vous êtes un assistant généraliste dont la tâche est de répondre à des questions générales."),
                     ("human", "{question}")]
                )
            elif mode == "ehs":
                prompt = ChatPromptTemplate.from_messages(
                    [("system", "Vous êtes un expert en EHS (Environnement, Hygiène et Sécurité)."),
                     ("human", "{question}")]
                )
            elif mode == "alcool":
                prompt = ChatPromptTemplate.from_messages(
                    [("system", "Tu es un assistant généraliste mais toutes tes réponses doivent posséder leurs lettres dans le désordre."),
                     ("human", "{question}")]
                )

            runnable = prompt | llm | StrOutputParser()
            cl.user_session.set("runnable", runnable)
            await Message(content=f"Le chatbot est prêt à être utilisé en mode **{mode}**. Posez vos questions !").send()
            return

    else:
        mode = cl.user_session.get("mode")
        runnable = cast(Runnable, cl.user_session.get("runnable"))

    if runnable is None and mode != "image":
        await Message(content="Erreur : Le chatbot n'a pas été correctement configuré. Veuillez redémarrer et choisir un mode.").send()
        return

    # Vérifier la langue du message et calculer les fautes si c'est en français
    langue = detect(message.content)
    pourcentage_fautes = 0
    if langue == "fr":
        pourcentage_fautes = calculer_fautes(message.content)

    msg = Message(content="")

    if mode == "image":
        try:
            model_id = "stability.stable-diffusion-xl-v1"
            native_request = {
                "text_prompts": [{"text": message.content, "weight": 1}],
                "cfg_scale": 10,
                "steps": 50,
                "seed": random.randint(0, 4294967295),  # Génère une seed aléatoire
                "width": 512,
                "height": 512,
                "samples": 1
            }
            request_body = json.dumps(native_request)
            response = client.invoke_model(
                modelId=model_id,
                contentType="application/json",
                accept="application/json",
                body=request_body
            )
            model_response = json.loads(response["body"].read())
            base64_image_data = model_response["artifacts"][0]["base64"]

            # Décoder les données de l'image encodée en base64
            image_bytes = base64.b64decode(base64_image_data)

            # Créer l'élément d'image
            image_element = Image(
                name="image.png",
                content=image_bytes,
                display="inline",
            )

            # Envoyer le message avec l'élément d'image attaché
            await Message(content="Voici l'image générée :", elements=[image_element]).send()

        except Exception as e:
            await Message(content="Erreur lors de la génération de l'image.").send()
            print(f"Erreur de génération d'image : {e}")
        return


    else:
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
