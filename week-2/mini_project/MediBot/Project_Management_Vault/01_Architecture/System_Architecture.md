# System Architecture

The MediBot system consists of three main pillars: a React frontend, a Django backend, and an AI RAG (Retrieval-Augmented Generation) pipeline.

## High-Level Architecture Diagram

```mermaid
graph TD
    Client[React Frontend - Vite + Tailwind] -->|REST API calls| API(Django API Gateway)
    
    subgraph Backend [Django Application]
        API --> AuthApp[Authentication App]
        API --> PatientApp[Patients App]
        API --> AIAgent[AI Agent App]
    end
    
    subgraph Data Layer [Database & Knowledge Base]
        AuthApp --> SQLite[(SQLite DB)]
        PatientApp --> SQLite
        
        AIAgent --> ChromaDB[(ChromaDB Vector Store)]
        AIAgent --> FAISS[(FAISS Index)]
        AIAgent --> LLM[External LLM / Internal Engine]
    end
    
    subgraph Knowledge Base Files
        TXT[Raw TXT Files] -->|Embedding| ChromaDB
        TXT -->|Embedding| FAISS
    end
```

## Components

1. **Frontend**: [[Frontend_Overview]]
2. **Backend**: [[Backend_Overview]]
3. **RAG Pipeline**: [[RAG_Knowledge_Base]]
