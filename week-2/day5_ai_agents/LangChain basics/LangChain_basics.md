# LangChain Quick Reference

## What is LangChain?
A framework for building AI apps (chatbots, RAG systems, agents, document Q&A) by connecting LLMs, prompts, tools, memory, vector DBs, and documents into reusable pipelines.

---

## Core Components

| Component | Purpose | Examples |
|---|---|---|
| **LLMs** | Connect to language models | OpenAI, Ollama, Gemini, Claude |
| **Prompts** | Reusable templates for model behavior | `"Answer using the provided context."` |
| **Chains** | Combine multiple steps into a workflow | Input → Prompt → LLM → Output |
| **Document Loaders** | Load external content | `PyPDFLoader`, `TextLoader`, `WebBaseLoader` |
| **Text Splitters** | Chunk large text for LLM limits | `RecursiveCharacterTextSplitter` |
| **Embeddings** | Convert text to vectors | OpenAI, HuggingFace, Ollama |
| **Vector Stores** | Store & search embeddings | Chroma, FAISS, Pinecone, Qdrant |
| **Retrievers** | Fetch relevant chunks from vector DBs | Core to RAG |
| **Memory** | Store conversation history | Buffer, summary, vector memory |
| **Agents** | LLMs that use tools dynamically | Calculator, search, APIs, DBs |

---

## Key Pipelines

**RAG Pipeline:**
```
Documents → Loader → Text Splitter → Embeddings → Vector Store → Retriever → LLM → Answer
```

**RAG Query Flow:**
```
Question → Retriever → Relevant Context → LLM → Final Answer
```

---

## Popular Modules

| Module | Purpose |
|---|---|
| `langchain_core` | Base components |
| `langchain_community` | Integrations |
| `langchain_text_splitters` | Chunking |
| `langchain_chroma` | Chroma DB |
| `langchain_ollama` | Local Ollama support |

---

## LangChain + Ollama (Local Setup)
```
Local Documents → LangChain → Ollama → Local AI Assistant
```
Benefits: runs locally, private, no API cost.

---

## Common Use Cases
- AI Chatbots
- PDF Q&A Systems
- Codebase / Research Assistants
- AI Agents

---

## Common Problems
- **Bad chunking** → poor retrieval
- **Hallucinations** → LLM invents answers
- **Large context** → too much irrelevant text
- **Slow retrieval** → large vector DBs

---

## LangChain vs Direct API

| Direct API | LangChain |
|---|---|
| Manual, low-level | Organized pipelines |
| More boilerplate | Reusable components |
| Flexible | Faster development |