from langchain_ollama import ChatOllama

# Step 1: Load local model
llm = ChatOllama(model="llama3")

# Step 2: Create reasoning prompt
prompt = """
Solve this problem step-by-step.

Question:
A laptop costs $1000.
It has a 10% discount.
After discount, add 5% tax.

What is the final price?
"""

# Step 3: Run model
response = llm.invoke(prompt)

# Step 4: Print reasoning + answer
print(response.content)