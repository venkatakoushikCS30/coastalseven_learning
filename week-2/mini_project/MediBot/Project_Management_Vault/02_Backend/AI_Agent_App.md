# AI Agent App

The `ai_agent` is a core Django application responsible for providing AI-driven features, specifically the RAG (Retrieval-Augmented Generation) capabilities of MediBot.

## Purpose
This app connects the user's queries from the frontend to the LLM, but first enriches the query by searching through the [[RAG_Knowledge_Base]].

## Key Files
- `services.py`: Contains the heavy lifting logic. This includes connecting to the LLM, embedding queries, and retrieving vectors from the database.
- `views.py`: Exposes REST API endpoints (e.g., `/api/ai_agent/query/`) that the [[Frontend_Overview|frontend]] calls.
- `models.py`: Stores metadata or chat history in the SQLite database.
- `test_voice_dictation.py`: A script within the backend context used to test voice-to-text features before integrating them into the agent.

## Database Integration
This app heavily relies on the external vector stores:
- **ChromaDB**: Located in the `chroma_db/` folder.
- **FAISS**: Located in the `faiss_indices/` folder.
