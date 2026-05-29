from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

# Load local Ollama model
llm = ChatOllama(
    model="llama3"
)

# Send message to model
response = llm.invoke(
    [
        HumanMessage(content="Explain semantic search in simple words")
    ]
)

# Print response
print(response.content)