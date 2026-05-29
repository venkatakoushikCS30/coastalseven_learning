from langchain_ollama import ChatOllama

# Step 1: Load local model
llm = ChatOllama(model="llama3")

# Step 2: Read input file
with open("input.txt", "r", encoding="utf-8") as file:
    content = file.read()

# Step 3: Create prompt
prompt = f"""
Summarize the following text in simple words:

{content}
"""

# Step 4: Send to AI
response = llm.invoke(prompt)

# Step 5: Save summary to file
with open("summary.txt", "w", encoding="utf-8") as file:
    file.write(response.content)

print("Summary saved successfully!")