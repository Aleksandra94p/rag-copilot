import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from chromadb import CloudClient
from .utils import chunk_text

_vectorstore = None

def get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        embeddings = SentenceTransformerEmbeddings(model_name="all-mpnet-base-v2")
        client = CloudClient(
            api_key=os.getenv("CHROMA_API_KEY"),
            tenant=os.getenv("CHROMA_TENANT"),
            database=os.getenv("CHROMA_DATABASE")
        )
        _vectorstore = Chroma(
            embedding_function=embeddings,
            client=client,
            collection_name="rag-data"
        )
    return _vectorstore

def add_file_to_db(filename: str, content: str):
    vs = get_vectorstore()
    existing_files = [m['source'] for m in vs.get()['metadatas']]
    if filename in existing_files:
        print(f"File '{filename}' already exists in the database.")
        return
    chunks = chunk_text(content)
    vs.add_texts(
        texts=chunks,
        metadatas=[{"source": filename} for _ in chunks]
    )
    print(f"File '{filename}' added as {len(chunks)} chunks.")

def refresh_chroma_db(file_paths: list):
    for path, content in file_paths:
        add_file_to_db(path, content)