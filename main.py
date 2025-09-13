import streamlit as st
from rag_agent import get_qa, add_file_to_db, get_repo_files, get_file_content, refresh_chroma_db, vectorstore

metadatas = vectorstore.get()['metadatas']
for m in metadatas:
    print(m['source'])


st.set_page_config(page_title="RAG Copilot", layout="wide")
st.title("RAG Copilot (Qwen2.5-Coder)")

st.header("Add Bitbucket File")
repo_files = get_repo_files(limit=5)
if repo_files:
    selected_file = st.selectbox("Select a file to fetch from Bitbucket:", repo_files)
    if st.button("Fetch and Add File"):
        if selected_file:
            content = get_file_content(selected_file)
            if content:
                add_file_to_db(selected_file, content)
                st.success(f"File '{selected_file}' added to Chroma database from Bitbucket!")
            else:
                st.error(f"Could not fetch content of {selected_file}.")
else:
    st.warning("No files fetched from Bitbucket. Check your API token and repo name.")

st.header("Add File to Chroma DB")
uploaded_file = st.file_uploader("Upload a text or code file", type=["txt", "py", "md"])

if uploaded_file:
    file_content = uploaded_file.read().decode("utf-8")
    filename = uploaded_file.name
    add_file_to_db(filename, file_content)
    st.success(f"File '{filename}' added to the Chroma database!")

st.header("Ask the RAG Agent")
user_question = st.text_area("Enter your question about the repository or code:")

if st.button("Get Answer"):
    qa = get_qa()
    if qa:
        with st.spinner("Generating answer..."):
            response = qa.run(user_question)
        st.subheader("Answer:")
        st.write(response)
    else:
        st.error("QA agent is not initialized. Make sure the vectorstore is ready!")


st.header("Chroma DB Sync")
if st.button("Refresh Chroma DB from Bitbucket"):
    with st.spinner("Refreshing Chroma DB..."):
        refresh_chroma_db()
    st.success("Chroma DB refreshed!")


st.header("Files in Chroma Database")
if st.button("Refresh File List"):
    metadatas = vectorstore.get()['metadatas']
    if metadatas:
        for m in metadatas:
            st.write(m['source'])
    else:
        st.info("No files in Chroma database yet.")