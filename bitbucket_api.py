import requests
from dotenv import load_dotenv
import os
from requests.auth import HTTPBasicAuth
 
load_dotenv()

BITBUCKET_USER = "aleksandra24"
BITBUCKET_API_TOKEN2 = os.getenv("BITBUCKET_API_TOKEN2")
REPO_SLUG = "rag-poc-test"
WORKSPACE = "zkr-hq"

def get_repo_files():
    url = f"https://api.bitbucket.org/2.0/repositories/{WORKSPACE}/{REPO_SLUG}/src/main/"
    response = requests.get(url, auth=HTTPBasicAuth(BITBUCKET_USER, BITBUCKET_API_TOKEN2))
    data = response.json()
    files = [f['path'] for f in data.get('values', [])]
    return files[:5]

def get_file_content(file_path):
    url = f"https://api.bitbucket.org/2.0/repositories/{WORKSPACE}/{REPO_SLUG}/src/main/{file_path}"
    response = requests.get(url, auth=(BITBUCKET_USER, BITBUCKET_API_TOKEN2))
    return response.text