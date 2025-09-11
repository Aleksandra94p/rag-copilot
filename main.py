import streamlit as st
from bitbucket_api import get_repo_files, get_file_content
from rag_agent import qa, add_file_to_db

st.title("RAG Copilot PoC")

add_file_to_db("primer.txt", "Ovo je test sadržaj")
print(qa) 
# Dugme za indeksiranje fajlova
if st.button("Index repo files"):
    files = get_repo_files()
    for f in files:
        content = get_file_content(f)
        add_file_to_db(f, content)
    st.success(f"Indexed {len(files)} files from repo")

# Polje za pitanje
query = st.text_input("Ask something about the repo:")

if query:
    answer = qa.run(query)
    st.code(answer)