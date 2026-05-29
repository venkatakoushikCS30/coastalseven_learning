from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

# Step 1: Load model
llm = ChatOllama(model="llama3")

# Step 2: Create prompt template
prompt = ChatPromptTemplate.from_template(
    "Explain {topic} in simple words"
)

# Step 3: Create workflow (chain)
workflow = prompt | llm

# Step 4: Run workflow
response = workflow.invoke(
    {
        "topic": "semantic search"
    }
)

# Step 5: Print output
print(response.content)