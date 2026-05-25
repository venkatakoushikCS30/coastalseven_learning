import requests

url = "http://localhost:11434/api/generate"

resume = """
Name: Koushik

Skills:
Python, Flask, MySQL, APIs

Experience:
Built a chatbot using Python and Streamlit.

Education:
B.Tech in Computer Science
"""

prompt = f"""
You are an HR assistant.

Analyze the following resume for a Backend Python Developer role.

Tasks:
1. Mention matching skills
2. Mention missing skills
3. Evaluate experience
4. Give final recommendation

Return response in bullet points.

Resume:
{resume}
"""

data = {
    "model": "gemma3:1b",
    "prompt": prompt,
    "stream": False,
    "options": {
        "temperature": 0.2
    }
}

response = requests.post(url, json=data)

result = response.json()

print("\nAI Analysis:\n")
print(result["response"])