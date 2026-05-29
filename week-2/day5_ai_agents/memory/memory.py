from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage

# Step 1: Load model
llm = ChatOllama(model="llama3")

# Step 2: Create memory list
memory = []

# Chat loop
while True:
    user_input = input("You: ")

    # Exit condition
    if user_input.lower() == "exit":
        break

    # Store user message in memory
    memory.append(HumanMessage(content=user_input))

    # Send full conversation history to model
    response = llm.invoke(memory)

    # Print AI response
    print("AI:", response.content)

    # Store AI response in memory
    memory.append(AIMessage(content=response.content))