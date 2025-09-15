from app.prompts import CODE_ASSIST_PROMPT
import os
import requests
from dotenv import load_dotenv

load_dotenv()

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
MODEL_NAME = "Qwen/Qwen2.5-Coder-1.5B-Instruct"

def query_llm(question: str, context: str):
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    prompt_text = CODE_ASSIST_PROMPT.format(context=context, question=question)
    payload = {
        "inputs": prompt_text,
        "parameters": {"max_new_tokens": 150, "temperature": 0.3}
    }
    url = f"https://api-inference.huggingface.co/models/{MODEL_NAME}"
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    if resp.status_code == 200:
        return resp.json()[0]["generated_text"]
    else:
        return f"Error: {resp.status_code} {resp.text}"