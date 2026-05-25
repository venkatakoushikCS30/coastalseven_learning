import requests

messages = []

while True:

    user_input = input("You: ")

    if user_input.lower() == "exit":
        break

    messages.append({
        "role": "user",
        "content": user_input
    })

    # Keep only last 3 messages
    messages = messages[-3:]

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "gemma3:1b",
            "messages": messages,
            "stream": False
        }
    )

    result = response.json()

    assistant_reply = result["message"]["content"]

    print("\nGemma:", assistant_reply)

    messages.append({
        "role": "assistant",
        "content": assistant_reply
    })
