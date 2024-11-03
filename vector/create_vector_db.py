import os
import asyncio
from langchain_aws import BedrockEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Configuration des embeddings Bedrock
embeddings = BedrockEmbeddings(
    credentials_profile_name="default",
    region_name="us-west-2",
    model_id='amazon.titan-embed-text-v2:0',
)

pdfs_directory = './documents'

# Fonction pour charger des documents à partir de fichiers PDF
async def load_documents_from_pdfs(file_path, province):
    print(f"Tentative de chargement du document : {file_path}")
    loader = PyPDFLoader(file_path)
    docs = await asyncio.to_thread(loader.load)  # Appel à la méthode load dans un thread
    # Ajout de la province comme métadonnée dans chaque document
    for doc in docs:
        doc.metadata['province'] = province
    print(f"Chargement terminé pour le document : {file_path}, nombre de pages chargées : {len(docs)}")
    return docs

# Fonction principale pour exécuter l'ensemble du processus
async def main():
    print("Chargement des documents depuis les fichiers PDF...")
    documents = []

    # Charger tous les fichiers PDF dans le répertoire spécifié
    pdf_count = 0
    for dirpath, _, filenames in os.walk(pdfs_directory):
        province = os.path.basename(dirpath)  # Obtenir le nom de la province
        print(f"Chargement des documents pour la province : {province}")
        for filename in filenames:
            if filename.endswith('.pdf'):
                pdf_count += 1
                file_path = os.path.join(dirpath, filename)  # Obtenir le chemin complet du fichier
                docs = await load_documents_from_pdfs(file_path, province)  # Appel pour charger les documents
                documents.extend(docs)  # Collecter les documents de tous les PDF

    # Vérifier si des documents ont été trouvés
    if not documents:
        print("Aucun document trouvé dans le répertoire fourni.")
        return

    print(f"Nombre total de documents chargés : {len(documents)} sur {pdf_count} PDF.")

    # Embedding des documents
    print("Génération des embeddings...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=20,
        length_function=len,
        is_separator_regex=False,
    )

    # Diviser les documents en morceaux tout en conservant les métadonnées
    chunked_documents = []
    for doc in documents:
        chunks = text_splitter.split_documents([doc])
        for chunk in chunks:
            # Garder les métadonnées originales (incluant la province)
            chunk.metadata = doc.metadata
        chunked_documents.extend(chunks)

    print(f"Documents divisés en morceaux, nombre total de morceaux : {len(chunked_documents)}.")

    # Créer une base de données Chroma à partir des documents
    print("Création de la base de données vectorielle à partir des documents...")
    db = Chroma.from_documents(chunked_documents, embeddings, persist_directory="my_embeddings/test2", collection_name="my_collection")

    # Persister les changements de la base de données
    db.persist()  # Sauvegarder les changements
    print("Base de données vectorielle créée avec succès dans le dossier : my_embeddings/test2")

# Exécution de la fonction principale
if __name__ == "__main__":
    asyncio.run(main())
