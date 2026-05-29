from langchain_ollama import ChatOllama
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType

# Load local model
llm = ChatOllama(model="llama3")

# Create a simple calculator tool
def calculator(expression):
    return str(eval(expression))

tools = [
    Tool(
        name="Calculator",
        func=calculator,
        description="Useful for solving math problems"
    )
]

# Create AI agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Run agent
response = agent.invoke(
    "What is 45 * 12 + 8?"
)

print(response)