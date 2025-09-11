import streamlit as st
from rag_agent import qa, add_file_to_db

st.set_page_config(page_title="RAG Copilot", layout="wide")
st.title("RAG Copilot (Qwen2.5-Coder)")


st.header("Add File to Chroma DB")
uploaded_file = st.file_uploader("Upload a text or code file", type=["txt", "py", "md"])

if uploaded_file:
    file_content = uploaded_file.read().decode("utf-8")
    filename = uploaded_file.name
    add_file_to_db(filename, file_content)
    st.success(f"File '{filename}' added to the database!")


st.header("Ask the RAG Agent")
user_question = st.text_area("Enter your question about the repository or code:")

if st.button("Get Answer"):
    if qa:
        response = qa.run(user_question)
        st.subheader("Answer:")
        st.write(response)
    else:
        st.error("QA agent is not initialized. Make sure the vectorstore is ready.")