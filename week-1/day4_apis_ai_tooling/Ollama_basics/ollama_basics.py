import ollama

response = ollama.chat(model="my-phi3-tutor",messages=[

{
    "role":"user",
    "content":"Explain the Model-View-Controller design pattern in one sentence.",
}

])
print(response['message']['content'])