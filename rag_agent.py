import os
from dotenv import load_dotenv
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI

# Učitavanje .env fajla
load_dotenv()  # učitava .env iz istog foldera
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print("OPENAI_API_KEY:", OPENAI_API_KEY)

# Inicijalizacija promenljivih
embeddings = None
vectorstore = None
qa = None

# Pokušavamo da inicijalizujemo embeddings, vectorstore i QA
try:
    if OPENAI_API_KEY:
        # Embedding model
        embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

        # Lokalna baza za vektore
        vectorstore = Chroma(persist_directory="chroma_db", embedding_function=embeddings)

        # QA chain
        qa = RetrievalQA.from_chain_type(
            llm=ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-3.5-turbo", temperature=0),
            retriever=vectorstore.as_retriever()
        )
    else:
        print("OPENAI_API_KEY nije definisan! qa neće biti kreiran.")
except Exception as e:
    print("Greška pri kreiranju qa ili vectorstore:", e)
    qa = None
    vectorstore = None

# Funkcija za dodavanje fajlova u Chroma bazu
def add_file_to_db(filename: str, content: str):
    if vectorstore:
        vectorstore.add_texts(
            texts=[content],
            metadatas=[{"source": filename}]
        )
        vectorstore.persist()
        print(f"Fajl '{filename}' dodat u Chroma bazu.")
    else:
        print(f"Vectorstore nije inicijalizovan. Ne mogu dodati fajl: {filename}")