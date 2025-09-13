import os
import streamlit as st
import requests
import chromadb
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.llms import HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, MapReduceDocumentsChain
from chromadb.config import Settings

load_dotenv()

MODEL_NAME = "Qwen/Qwen2.5-Coder-1.5B-Instruct" 
EMBEDDING_MODEL = "all-mpnet-base-v2"
BITBUCKET_USER = "aleksandra24"
BITBUCKET_API_TOKEN = os.getenv("BITBUCKET_API_TOKEN")
REPO_SLUG = "rag-data"
WORKSPACE = "zkr-hq"

import chromadb
  
prompt_template = """You are an AI programming assistant. Use the provided context to answer the question accurately.
If the answer is not in the context, say "I don't know".

Context:
{context}

Question:
{question}

If the question is about code, suggest code snippets or improvements.
If the question is about a bug or error, identify the problem and suggest a fix.
If the question is about architecture or documentation, provide a clear explanation.

Answer:"""
PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=prompt_template
)

@st.cache_resource
def get_llm():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        device_map="auto",
        torch_dtype="auto"
    )
    text_gen = pipeline(
        task="text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=150,  
        temperature=0.3
    )
    return HuggingFacePipeline(pipeline=text_gen)


@st.cache_resource
def get_vectorstore():
    embeddings = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL)

    client = chromadb.CloudClient(
    api_key=os.getenv("CHROMA_API_KEY"),
    tenant=os.getenv("CHROMA_TENANT"),
    database=os.getenv("CHROMA_DATABASE")
)

    vectorstore = Chroma(
        embedding_function=embeddings,
        client=client,
        collection_name="rag-data"
    )
    return vectorstore

vectorstore = get_vectorstore()

@st.cache_resource
def get_qa():
    llm = get_llm()
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 1}),
        chain_type="stuff",  # može biti 'stuff', 'map_reduce' ili 'refine'
        chain_type_kwargs={"prompt": PROMPT},
        return_source_documents=False
    )
    return qa

qa = get_qa()

def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def refresh_chroma_db(limit=20):
   
    repo_files = get_repo_files(limit=limit)
    for file_path in repo_files:
        existing_files = [m['source'] for m in vectorstore.get()['metadatas']]
        if file_path not in existing_files:
            content = get_file_content(file_path)
            if content:
                add_file_to_db(file_path, content)
                print(f"Added {file_path} to Chroma DB.")
            else:
                print(f"Could not fetch content for {file_path}.")
        else:
            print(f"{file_path} already in Chroma DB.")


def add_file_to_db(filename: str, content: str):
  
    existing_files = [m['source'] for m in vectorstore.get()['metadatas']]
    if filename in existing_files:
        print(f"File '{filename}' already exists in the database.")
        return

    chunks = chunk_text(content)
    vectorstore.add_texts(
        texts=chunks,
        metadatas=[{"source": filename} for _ in chunks]
    )
    
    print(f"File '{filename}' added to Chroma database as {len(chunks)} chunks.")

def get_repo_files(limit=5):
    
    url = f"https://api.bitbucket.org/2.0/repositories/{WORKSPACE}/{REPO_SLUG}/src/main/"

    headers = {
        "Authorization": f"Bearer {BITBUCKET_API_TOKEN}",
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching repo files: {e}")
        return []

    try:
        data = response.json()
        files = [f['path'] for f in data.get('values', [])]
        return files[:limit]
    except ValueError as e:
        print(f"JSON parsing error: {e}")
        return []

def get_file_content(file_path):
    
    url = f"https://api.bitbucket.org/2.0/repositories/{WORKSPACE}/{REPO_SLUG}/src/main/{file_path}"

    headers = {
        "Authorization": f"Bearer {BITBUCKET_API_TOKEN}",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching file {file_path}: {e}")
        return ""