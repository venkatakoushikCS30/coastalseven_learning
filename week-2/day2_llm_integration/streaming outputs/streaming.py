import requests
import json

url = "http://localhost:11434/api/generate"

data = {
    "model": "gemma3:1b",
    "prompt": "Explain neural networks",
    "stream": True
}

response = requests.post(
    url,
    json=data,
    stream=True
)

for line in response.iter_lines():

    if line:

        decoded_line = line.decode("utf-8")

        json_data = json.loads(decoded_line)

        print(json_data["response"], end="")