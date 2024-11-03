import chainlit as cl
from langchain_aws import ChatBedrockConverse
from langchain.prompts import ChatPromptTemplate, PromptTemplate
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
from langchain_aws import BedrockEmbeddings
from metadata_filtered_retriever import MetadataFilteredRetriever
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

# Initialiser le correcteur orthographique pour le français
spell = SpellChecker(language="fr")

# Fonction pour calculer le pourcentage de fautes d'orthographe
def calculer_fautes(message):
    print("Calcul du pourcentage de fautes...")
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
    
    ehs = ChatBedrockConverse(
        model="anthropic.claude-3-sonnet-20240229-v1:0",
        region_name="us-west-2",
        temperature=0,
        max_tokens=None
    )

    embeddings = BedrockEmbeddings(
        credentials_profile_name="default",
        region_name="us-west-2",
        model_id='amazon.titan-embed-text-v2:0',
    )

    # Initialize the retriever manager
    retriever_manager = MetadataFilteredRetriever(
        embeddings=embeddings,
        persist_directory="../vector/my_embeddings/test2",
        collection_name="my_collection"
    )
    
    # Create different retrievers for different contexts
    retrievers = {
        "quebec": retriever_manager.get_retriever(province="quebec"),
        "default": retriever_manager.get_retriever(province="general"),
    }
    
    # Store all necessary elements in the session
    cl.user_session.set("retrievers", retrievers)
    cl.user_session.set("ehs", ehs)
    cl.user_session.set("current_retriever", "default")  # Set default context

    await Message(
        content="Bonjour ! Souhaitez-vous utiliser le chatbot en version **généraliste**, **EHS**, ou pour générer une **image** ?"
    ).send()

@cl.on_message
async def on_message(message: Message):
    # Vérifier si l'utilisateur veut changer de mode
    if message.content.startswith("changer de mode"):
        cl.user_session.set("mode", None)  # Réinitialise le mode pour forcer un nouveau choix
        cl.user_session.set("runnable", None)  # Supprime l'ancien runnable
        nouveau_mode = message.content.split(" ", 1)[1].strip().lower()
        if nouveau_mode in ["généraliste", "ehs", "image", "alcool"]:
            await Message(content=f"Vous avez choisi de passer en mode **{nouveau_mode}**. Veuillez confirmer en posant une question.").send()
            return
        else:
            await Message(content="Veuillez choisir entre 'généraliste', 'ehs', 'image' ou 'alcool'.").send()
            return
    
    # Initialiser le client Bedrock pour toutes les opérations
    client = boto3.client("bedrock-runtime", region_name="us-west-2")

    # Vérifier si le mode est déjà stocké dans la session
    mode = cl.user_session.get("mode")

    # Récupérer les éléments nécessaires
    retrievers = cl.user_session.get("retrievers")
    current_retriever = cl.user_session.get("current_retriever")


    # Check if the message contains a command to change context
    if message.content.startswith("/context"):
        new_context = message.content.split()[1]
        if new_context in retrievers:
            cl.user_session.set("current_retriever", new_context)
            await cl.Message(content=f"Switched to {new_context} context.").send()
            return
        else:
            await cl.Message(content="Invalid context. Available contexts: " + 
                            ", ".join(retrievers.keys())).send()
            return

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
            await Message(content="Le chatbot est prêt à générer des images. Décrivez l'image que vous souhaitez obtenir !").send()
            return

        else:
            # Initialiser le LLM pour les autres modes (déplacé ici pour une meilleure logique)
            llm = ChatBedrockConverse(
                model="anthropic.claude-3-sonnet-20240229-v1:0",
                region_name="us-west-2",
                temperature=0,
                max_tokens=None
            )
            print(f"Mode choisi : {mode}")

            if mode == "généraliste":
                prompt = ChatPromptTemplate.from_messages(
                    [("system", "Vous êtes un assistant généraliste dont la tâche est de répondre à des questions générales."),
                     ("human", "{question}")]
                )
            elif mode == "ehs":
                # Create and execute the RAG chain with the current retriever
                ehs = cl.user_session.get("ehs")
                rag_chain = create_chain(ehs, retrievers[current_retriever])
                res = rag_chain.invoke(message.content)
                await cl.Message(content=res).send()
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

    # Logique pour la réponse de l'assistant
    try:
        if mode == "image":
            # Logique pour la génération d'images serait ici
            await Message(content="La génération d'images n'est pas encore implémentée.").send()
        elif mode == "généraliste":
            prompt = ChatPromptTemplate.from_messages(
                [("system", "Vous êtes un assistant généraliste dont la tâche est de répondre à des questions générales."),
                ("human", "{question}")]
            )
        elif mode == "ehs":
            # Créez et exécutez la chaîne RAG avec le récupérateur actuel
            ehs = cl.user_session.get("ehs")
            rag_chain = create_chain(ehs, retrievers[current_retriever])
            res = rag_chain.invoke(message.content)
            await cl.Message(content=res).send()  # Assurez-vous que send() est une coroutine
            prompt = ChatPromptTemplate.from_messages(
                [("system", "Vous êtes un expert en EHS (Environnement, Hygiène et Sécurité)."),
                ("human", "{question}")]
            )
        elif mode == "alcool":
            prompt = ChatPromptTemplate.from_messages(
                [("system", "Tu es un assistant généraliste mais toutes tes réponses doivent posséder leurs lettres dans le désordre."),
                ("human", "{question}")]
            )
        else:
            response = await runnable.invoke(message.content)  # Invoke the runnable
            pourcentage_fautes = calculer_fautes(response)

            if pourcentage_fautes > 20:
                response = deform_response(response)

            await Message(content=response).send()  # Assurez-vous que send() est une coroutine

    except Exception as e:
        print(f"Erreur lors de l'invocation du modèle : {e}")
        await Message(content="Une erreur est survenue lors de la génération de la réponse.").send()  # Assurez-vous que send() est une coroutine

def create_chain(llm, retriever):
    """Creates a RAG chain for processing queries."""
    template = """
    You are an assistant. Use the following pieces of retrieved context to answer the question.\n
    If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.\n
    Question: {question}\n
    Context: {context}\n
    Answer: """
    
    prompt = PromptTemplate(template=template, input_variables=['question', 'context'])
    
    def format_docs(docs):
        """Formats retrieved documents for the prompt."""
        return "\n\n".join(doc.page_content for doc in docs)

    # Create chain
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain
