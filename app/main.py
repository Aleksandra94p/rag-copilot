from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from app.repo import get_repo_files, get_file_content
from app.vectorstore import get_vectorstore, add_file_to_db, refresh_chroma_db
from app.llm import query_llm

app = FastAPI(title="RAG Copilot Backend")

class Question(BaseModel):
    question: str

@app.get("/files")
def list_files(limit: int = 10):
    return {"files": get_repo_files(limit)}

@app.post("/refresh")
def refresh_db(limit: int = 20):
    files = [(f, get_file_content(f)) for f in get_repo_files(limit)]
    refresh_chroma_db(files)
    return {"status": "Chroma DB refreshed"}

@app.post("/upload")
def upload_file(file: UploadFile = File(...)):
    content = file.file.read().decode("utf-8")
    add_file_to_db(file.filename, content)
    return {"status": f"File {file.filename} added to Chroma DB"}

@app.post("/ask")
def ask_question(q: Question):
    vs = get_vectorstore()
    retriever = vs.as_retriever(search_kwargs={"k": 1})
    docs = retriever.get_relevant_documents(q.question)
    context = " ".join([doc.page_content for doc in docs])
    answer = query_llm(q.question, context)
    return {"answer": answer}

