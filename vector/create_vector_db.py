import os
import asyncio
from langchain_aws import BedrockEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader

# Configuration des embeddings Bedrock
embeddings = BedrockEmbeddings(
    credentials_profile_name="default",
    region_name="us-west-2",
    model_id='amazon.titan-embed-text-v2:0',
)

pdfs_directory = './documents'

# Fonction pour charger des documents à partir de fichiers PDF
async def load_documents_from_pdfs(file_path):
    loader = PyPDFLoader(file_path)
    pages = []
    async for page in loader.alazy_load():  # Fixed indentation
        pages.append(page)
    return pages  # Added return statement

# Fonction d'embedding des documents
async def embed_documents(documents):
    # Embedding de tous les documents
    document_embeddings = await embeddings.aembed_documents([doc.page_content for doc in documents])
    return document_embeddings

# Fonction principale pour exécuter l'ensemble du processus
async def main():
    # Charger les documents depuis les fichiers PDF
    print("Chargement des documents depuis les fichiers PDF...")
    documents = []

    # Charger tous les fichiers PDF dans le répertoire spécifié
    for filename in os.listdir(pdfs_directory):
        if filename.endswith('.pdf'):
            file_path = os.path.join(pdfs_directory, filename)
            docs = await load_documents_from_pdfs(file_path)  # Call to load documents
            documents.extend(docs)  # Collect documents from all PDFs

    # Vérifier si des documents ont été trouvés
    if not documents:
        print("Aucun document trouvé dans le répertoire fourni.")
        return

    # Embedding des documents
    print("Génération des embeddings...")
    document_embeddings = await embed_documents(documents)

    # Créer une instance Chroma DB pour stocker les embeddings
    db = Chroma(persist_directory="chroma_langchain_db", embedding_function=embeddings)

    # Ajouter les documents et leurs embeddings à Chroma
    print("Ajout des documents à la base de données vectorielle...")
    db.add_documents(documents=document_embeddings)
    db.persist()  # Sauvegarder les changements

    print("Base de données vectorielle créée avec succès dans le dossier : chroma_langchain_db")

# Exécution de la fonction principale
if __name__ == "__main__":
    asyncio.run(main())
