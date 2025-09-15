import os
import requests
from dotenv import load_dotenv

load_dotenv()

BITBUCKET_USER = "aleksandra24"
BITBUCKET_API_TOKEN = os.getenv("BITBUCKET_API_TOKEN")
REPO_SLUG = "rag-data"
WORKSPACE = "zkr-hq"

def get_repo_files(limit: int = 5):
    url = f"https://api.bitbucket.org/2.0/repositories/{WORKSPACE}/{REPO_SLUG}/src/main/"
    headers = {"Authorization": f"Bearer {BITBUCKET_API_TOKEN}", "Accept": "application/json"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        files = [f['path'] for f in data.get('values', [])]
        return files[:limit]
    except Exception as e:
        print(f"Error fetching repo files: {e}")
        return []

def get_file_content(file_path: str):
    url = f"https://api.bitbucket.org/2.0/repositories/{WORKSPACE}/{REPO_SLUG}/src/main/{file_path}"
    headers = {"Authorization": f"Bearer {BITBUCKET_API_TOKEN}", "Accept": "application/json"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"Error fetching file {file_path}: {e}")
        return ""