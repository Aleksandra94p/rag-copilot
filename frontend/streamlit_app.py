import streamlit as st
import requests

BACKEND_URL = "https://rag-copilot-for-wwft-repo.onrender.com"

st.set_page_config(page_title="RAG Copilot", layout="wide")
st.title("RAG Copilot (Qwen2.5-Coder)")

st.header("Bitbucket Repository Files")
if st.button("Fetch Files"):
    resp = requests.get(f"{BACKEND_URL}/files")
    files = resp.json().get("files", [])
    for f in files:
        st.write(f)

st.header("Upload File to Chroma DB")
uploaded_file = st.file_uploader("Select a file", type=["txt", "py", "md"])
if uploaded_file:
    if st.button("Upload File"):
        files = {"file": (uploaded_file.name, uploaded_file.read())}
        resp = requests.post(f"{BACKEND_URL}/upload", files=files)
        st.success(resp.json().get("status"))

st.header("Ask the RAG Agent")
question = st.text_area("Enter your question:")
if st.button("Get Answer"):
    resp = requests.post(f"{BACKEND_URL}/ask", json={"question": question})
    st.write("Status code:", resp.status_code)
    st.write("Raw response:", resp.text)
    if resp.headers.get("content-type") == "application/json":
        answer = resp.json().get("answer")
        st.write(answer)
    else:
        st.error("Ask endpoint did not return JSON")

st.header("Chroma DB Sync")
if st.button("Refresh DB"):
    resp = requests.post(f"{BACKEND_URL}/refresh")
    st.success(resp.json().get("status"))