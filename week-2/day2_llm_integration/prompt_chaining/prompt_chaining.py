import requests

url = "http://localhost:11434/api/generate"

# STEP 1
prompt1 = "Extract skills from: Python, Flask, MySQL developer"

response1 = requests.post(
    url,
    json={
        "model": "gemma3:1b",
        "prompt": prompt1,
        "stream": False
    }
)

skills = response1.json()["response"]

print("\nExtracted Skills:\n", skills)

# STEP 2
prompt2 = f"""
Generate 3 interview questions for these skills:

{skills}
"""

response2 = requests.post(
    url,
    json={
        "model": "gemma3:1b",
        "prompt": prompt2,
        "stream": False
    }
)

questions = response2.json()["response"]

print("\nInterview Questions:\n")
print(questions)