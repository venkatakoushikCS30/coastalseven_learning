from langchain_ollama import ChatOllama
from langchain.agents import Tool, initialize_agent
from langchain.agents import AgentType

# Step 1: Load local model
llm = ChatOllama(model="llama3")

# Step 2: Create custom tool
def calculator(expression):
    return str(eval(expression))

# Step 3: Convert function into Tool
calculator_tool = Tool(
    name="Calculator",
    func=calculator,
    description="Useful for solving math calculations"
)

# Step 4: Create agent with tool
agent = initialize_agent(
    tools=[calculator_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Step 5: Ask question
response = agent.invoke(
    "What is 25 * 4 + 10?"
)

# Step 6: Print result
print(response)