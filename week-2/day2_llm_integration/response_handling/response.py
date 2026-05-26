import requests
import json

# Send prompt to LLM
response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "gemma3:1b",
        "prompt": "What is Python?",
        "stream": False
    }
)

# Handle errors
if response.status_code != 200:
    print("Error:", response.status_code)
else:
    # Extract response
    result = response.json()
    answer = result["response"]
    
    # Display
    print(answer)