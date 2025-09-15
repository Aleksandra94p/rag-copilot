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

st.header("Ask the RAG Agent")
question = st.text_area("Enter your question:")

if st.button("Get Answer"):
    if not question.strip():
        st.warning("Please enter a question first!")
    else:
        try:
            resp = requests.post(f"{BACKEND_URL}/ask", json={"question": question}, timeout=10)
            st.write("Status code:", resp.status_code)
            st.write("Raw response:", resp.text)

            # Provera da li je odgovor JSON
            if "application/json" in resp.headers.get("content-type", ""):
                data = resp.json()
                answer = data.get("answer")
                if answer:
                    st.success(answer)
                else:
                    st.warning("Backend returned JSON but no 'answer' field found.")
            else:
                st.error("Backend did not return JSON. Check backend logs.")

        except requests.exceptions.Timeout:
            st.error("Request timed out. Please try again later.")
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to backend. Is it running?")
        except requests.exceptions.RequestException as e:
            st.error(f"An unexpected error occurred: {e}")
        except ValueError as e:  # hvata JSONDecodeError
            st.error(f"Failed to parse JSON response: {e}")
            
st.header("Chroma DB Sync")
if st.button("Refresh DB"):
    resp = requests.post(f"{BACKEND_URL}/refresh")
    st.success(resp.json().get("status"))