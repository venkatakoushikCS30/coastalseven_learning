# Abbreviations and Glossary

A reference guide for the acronyms, abbreviations, and domain-specific terminology used across the MediBot project.

## A-C
- **API** (Application Programming Interface): A set of rules that allows the [[Frontend_Overview|frontend]] to talk to the [[Backend_Overview|backend]].
- **ASGI** (Asynchronous Server Gateway Interface): The async python web server specification used by Django for WebSockets/async features.
- **ChromaDB**: An open-source vector database used in MediBot for storing and querying AI embeddings.

## D-H
- **Django**: The high-level Python web framework used for the MediBot backend.
- **ERD** (Entity-Relationship Diagram): A structural diagram used in [[SDLC|System Design]] to model the database tables (e.g., Patients, Users).
- **FAISS** (Facebook AI Similarity Search): A library for efficient similarity search and clustering of dense vectors, used alongside ChromaDB.
- **HIPAA**: Health Insurance Portability and Accountability Act (a regulatory standard for protecting sensitive patient data).

## I-M
- **LLM** (Large Language Model): The core AI engine that processes text and generates responses for the MediBot user.
- **MCP** (Model Context Protocol): A standardized protocol for providing context (like files or database records) to Large Language Models, potentially used for integrating external tools with the AI Agent.

## N-R
- **RAG** (Retrieval-Augmented Generation): An AI technique where the LLM queries an external knowledge base (our text files) to ground its responses in factual data. See [[RAG_Knowledge_Base]].
- **React**: The JavaScript library used for building the MediBot user interface.

## S-Z
- **SDLC** (Software Development Life Cycle): The process used to design, develop, and test high-quality software. See [[SDLC]].
- **Vite**: The fast build tool and development server used for the MediBot React frontend.
- **WSGI** (Web Server Gateway Interface): The standard synchronous Python web server specification used by Django.
