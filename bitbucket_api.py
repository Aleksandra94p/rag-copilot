import requests

BITBUCKET_USER = "aleksandra24"
BITBUCKET_API_TOKEN = "ATATT3xFfGF0SqpcoTxvFqOeqyu5kAHcNUUxzmCAY0yx_rjOKgKSpDmLHzVAZaKP9TZIP0Ci0UWvevu9qmYvPAc6duAOujHZW5Tuw8Apjn0tXpb5ho8yfHmP3S_7U-tacvKDKpZYanUKROB6mpUaEM9ici32xmlmDop16QUYxIw_IfQg-K4w8Vw=0825F176"
REPO_SLUG = "rag-poc-test"
WORKSPACE = "zkr-hq"

def get_repo_files():
    url = f"https://api.bitbucket.org/2.0/repositories/{WORKSPACE}/{REPO_SLUG}/src/main/"
    response = requests.get(url, auth=(BITBUCKET_USER, BITBUCKET_API_TOKEN))
    data = response.json()
    files = [f['path'] for f in data.get('values', [])]
    return files[:5]

def get_file_content(file_path):
    url = f"https://api.bitbucket.org/2.0/repositories/{WORKSPACE}/{REPO_SLUG}/src/main/{file_path}"
    response = requests.get(url, auth=(BITBUCKET_USER, BITBUCKET_API_TOKEN))
    return response.text 