import requests

url = "http://localhost:11434/api/generate"

data = {
    "model": "gemma3:1b",
    "prompt": "Explain AI in simple terms",
    "stream": False,
    "options": {
        "temperature": 0.2
    }
}

response = requests.post(url, json=data)

print(response.json()["response"])