# Connecting Python Apps with Ollama APIs

## Overview

**Ollama** enables running Large Language Models (LLMs) locally. With Python, you can build AI chatbots, resume analyzers, PDF assistants, coding tools, RAG systems, and automation tools.

**Popular Models:** Gemma, Llama, Mistral, DeepSeek

---

## Setup & Installation

### 1. Install Ollama
Download from [ollama.com](https://ollama.com) and install for your OS.

### 2. Pull a Model
```bash
ollama pull gemma3:1b
```

### 3. Verify Installation
```bash
ollama run gemma3:1b
# Type: "Explain machine learning"
```

### 4. Install Python Dependencies
```bash
pip install requests
```

---

## How Ollama Works

```
Python App → HTTP Request → Ollama Server (localhost:11434) → LLM Model → Response
```

Ollama runs on **localhost:11434** and exposes RESTful APIs for inference.

---

## Core APIs

| Endpoint | Purpose |
|----------|---------|
| `/api/generate` | Single prompt generation |
| `/api/chat` | Multi-turn conversations |
| `/api/tags` | List installed models |
| `/api/show` | Model details |

---

## Basic Usage

### Generate API (Single Prompt)

```python
import requests

url = "http://localhost:11434/api/generate"

data = {
    "model": "gemma3:1b",
    "prompt": "Explain APIs in simple words",
    "stream": False
}

response = requests.post(url, json=data)
print(response.json()["response"])
```

### Streaming Response
For real-time token-by-token output (like ChatGPT):

```python
import requests
import json

url = "http://localhost:11434/api/generate"
data = {
    "model": "gemma3:1b",
    "prompt": "Explain neural networks",
    "stream": True
}

response = requests.post(url, json=data, stream=True)

for line in response.iter_lines():
    if line:
        print(json.loads(line.decode("utf-8"))["response"], end="")
```

---

## Chat API (Conversations)

### Single Turn
```python
import requests

url = "http://localhost:11434/api/chat"

messages = [{"role": "user", "content": "My name is Alice"}]

response = requests.post(url, json={
    "model": "gemma3:1b",
    "messages": messages,
    "stream": False
})

print(response.json())
```

### Multi-Turn Chatbot
```python
import requests

url = "http://localhost:11434/api/chat"
messages = []

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break
    
    messages.append({"role": "user", "content": user_input})
    
    response = requests.post(url, json={
        "model": "gemma3:1b",
        "messages": messages,
        "stream": False
    })
    
    assistant_reply = response.json()["message"]["content"]
    print(f"\nGemma: {assistant_reply}\n")
    messages.append({"role": "assistant", "content": assistant_reply})
```

---

## Advanced Features

### System Prompting
Control AI behavior with system messages:

```python
messages = [
    {"role": "system", "content": "You are a strict Python interviewer."},
    {"role": "user", "content": "What is a decorator?"}
]
```

System prompts define: **tone**, **personality**, **behavior**, **response style**

### Temperature Control
```python
"options": {"temperature": 0.2}  # Low: factual, stable
"options": {"temperature": 0.8}  # High: creative, diverse
```

**Use cases:**
- **Low (0.0-0.3):** Coding, analysis, APIs
- **High (0.7-1.0):** Storytelling, brainstorming

### List Models
```python
import requests
response = requests.get("http://localhost:11434/api/tags")
print(response.json())
```

### Show Model Info
```python
import requests
response = requests.post("http://localhost:11434/api/show", 
    json={"name": "gemma3:1b"})
print(response.json())
```

---

## Production Architecture

### FastAPI Integration
```python
from fastapi import FastAPI
import requests

app = FastAPI()

@app.get("/chat")
def chat(prompt: str):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "gemma3:1b",
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()
```

### Typical Stack
```
Frontend → Backend (FastAPI/Flask) → Ollama API → LLM Model
```

---

## Common Issues & Fixes

| Error | Cause | Solution |
|-------|-------|----------|
| **Connection Refused** | Ollama not running | Start Ollama |
| **Model Not Found** | Model not downloaded | `ollama pull gemma3:1b` |
| **Slow Responses** | CPU inference | Use smaller models / GPU |
| **High RAM Usage** | Large models | Use lighter models |

---

## Key Concepts

- **You perform inference**, not training—using pretrained models
- **Streaming** improves UX by showing output in real-time
- **Conversation memory** is maintained via message history in `/api/chat`
- **Temperature** controls randomness/creativity

---

## Advantages vs Limitations

### ✅ Advantages
- Free local AI (no API costs)
- Privacy-focused & offline
- Easy model management
- Supports multiple LLMs

### ❌ Limitations
- Slower without GPU
- High RAM for large models
- Local storage requirements
- Limited compared to cloud GPUs

---

## What You Can Build

- AI chatbots
- Resume analyzers
- PDF assistants
- Coding assistants
- AI agents
- Automation systems
- Knowledge assistants
- Custom AI tools

---

## Next Steps to Learn

1. **RAG Systems** & Embeddings
2. **Vector Databases** (Pinecone, Weaviate)
3. **LangChain** integration
4. **AI Agents** & tool calling
5. **Fine-tuning** LLMs
6. **Advanced Prompt Engineering**
7. **FastAPI AI Deployment**
8. **Local AI Architectures**

---

## Quick Reference

```python
# Basic imports
import requests
import json

# Ollama base URL
BASE_URL = "http://localhost:11434"

# Common models
MODELS = ["gemma3:1b", "mistral", "llama2"]

# Generate endpoint
requests.post(f"{BASE_URL}/api/generate", json={...})

# Chat endpoint
requests.post(f"{BASE_URL}/api/chat", json={...})
```