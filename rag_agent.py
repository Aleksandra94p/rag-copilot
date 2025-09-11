from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.llms import HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

# ---------------------------
# Embeddings
# ---------------------------
embeddings = SentenceTransformerEmbeddings(model_name="all-mpnet-base-v2")

# ---------------------------
# Vectorstore (Chroma)
# ---------------------------
vectorstore = Chroma(
    persist_directory="chroma_db",
    embedding_function=embeddings
)

# ---------------------------
# Hugging Face Qwen2.5-Coder model
# ---------------------------
model_name = "Qwen/Qwen2.5-Coder-7B-Instruct"  # or "Qwen/Qwen2.5-Coder-32B-Instruct" for more powerfull version

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
    torch_dtype="auto"
)

text_gen = pipeline(
    task="text-generation",
    model=model,
    tokenizer=tokenizer,
    max_length=1024,
    temperature=0
)

llm = HuggingFacePipeline(pipeline=text_gen)


qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever()
)

def add_file_to_db(filename: str, content: str):
    if vectorstore:
        vectorstore.add_texts(
            texts=[content],
            metadatas=[{"source": filename}]
        )
        vectorstore.persist()
        print(f"File '{filename}' added to Chroma database.")
    else:
        print(f"Vectorstore not initialized. Cannot add file: {filename}")