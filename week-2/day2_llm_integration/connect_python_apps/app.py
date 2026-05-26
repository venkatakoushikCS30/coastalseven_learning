import requests

url = "http://localhost:11434/api/chat"

messages = []

while True:

    user_input = input("You: ")

    if user_input.lower() == "exit":
        break

    messages.append({
        "role": "user",
        "content": user_input
    })

    response = requests.post(
        url,
        json={
            "model": "gemma3:1b",
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.9,
            }
        }
    )

    result = response.json()

    assistant_reply = result["message"]["content"]

    print("\nGemma:", assistant_reply)

    messages.append({
        "role": "assistant",
        "content": assistant_reply
    })
