# MediBot

MediBot is an AI-powered application designed to assist with patient management, medical knowledge retrieval, and voice dictation.

## Project Structure

This project is divided into several main components:

- **`frontend/`**: A modern React application built with Vite and Tailwind CSS. It provides the user interface for the platform.
- **`backend/`**: A Django-based REST API that handles user authentication, patient records, and integrates with the AI services.
- **`knowledge_base/`**: Contains documents and data used by the AI agent for Retrieval-Augmented Generation (RAG).
- **`Project_Management_Vault/`**: An Obsidian vault for project documentation and task management.

## Key Features

- **Patient Management**: Secure backend system to manage patient records (`patients` app).
- **AI Agent**: Intelligent assistant with vector database integration (ChromaDB & FAISS) for querying medical knowledge.
- **Voice Dictation**: Capabilities for voice-to-text dictation.
- **Authentication**: Secure user authentication and authorization (`authentication` app).

## Tech Stack

- **Frontend**: React 19, Vite, Tailwind CSS, React Router
- **Backend**: Python, Django, SQLite (for development)
- **AI & Vector DBs**: FAISS, ChromaDB

## Getting Started

### Prerequisites

- Python 3.x
- Node.js and npm

### Backend Setup

1. Activate the virtual environment:
   ```bash
   # Windows
   .\venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```
2. Navigate to the backend directory:
   ```bash
   cd backend
   ```
3. Run database migrations:
   ```bash
   python manage.py migrate
   ```
4. Start the development server:
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install the necessary dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
