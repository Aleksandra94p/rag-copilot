import os
import streamlit as st
import requests
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.llms import HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from requests.auth import HTTPBasicAuth
from langchain.prompts import PromptTemplate



load_dotenv()

MODEL_NAME = "Qwen/Qwen2.5-Coder-1.5B-Instruct" 
CHROMA_DIR = "chroma_db"
EMBEDDING_MODEL = "all-mpnet-base-v2"

BITBUCKET_USER = "aleksandra24"
BITBUCKET_API_TOKEN = os.getenv("BITBUCKET_API_TOKEN")
REPO_SLUG = "rag-data"
WORKSPACE = "zkr-hq"

print(os.getenv("BITBUCKET_API_TOKEN"))

prompt_template = ""

PROMPT = PromptTemplate(
    input_variables=["context",  "question"],
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
    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings
    )
    return vectorstore

vectorstore = get_vectorstore()

@st.cache_resource
def get_qa():
    llm = get_llm()
    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 1}), #koliko dokumenata se uzima, kasnije mozes da povecas broj dokumenata
        chain_type = "stuff", # "map_reduce" uzima svaki dokumet posebno pa kombinuje, trebace kasnije
        return_source_documents=False,
        chain_type_kwargs={"prompt": PROMPT}  
    )

qa = get_qa()

def add_file_to_db(filename: str, content: str):
    """
    Adds a text file to the Chroma vectorstore with the metadata 'source'.
    If the file already exists, it will not be added again.
    """
    existing_files = [m['source'] for m in vectorstore.get()['metadatas']]
    if filename in existing_files:
        print(f"File '{filename}' already exists in the database.")
        return

    vectorstore.add_texts(
        texts=[content],
        metadatas=[{"source": filename}]
    )
    vectorstore.persist()
    print(f"File '{filename}' added to Chroma database.")

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