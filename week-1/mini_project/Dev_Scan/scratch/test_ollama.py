# scratch/test_ollama.py
import requests
import json

url = "http://localhost:11434/api/chat"
payload = {
    "model": "devscan-ai",
    "messages": [{"role": "user", "content": "Hello"}],
    "stream": False
}

try:
    print("Sending request to Ollama with timeout=None...")
    res = requests.post(url, json=payload, timeout=None)
    print("Status code:", res.status_code)
    print("Response JSON:", res.json())
except Exception as e:
    print("Error:", e)
