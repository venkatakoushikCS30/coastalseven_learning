# Development Workflow

This document outlines the standard day-to-day workflow for a developer working on the MediBot project.

## Local Setup

### 1. Start the Backend
The backend runs on Django and requires a Python virtual environment.
```bash
# Open terminal
cd MediBot
# Activate virtual environment
.\venv\Scripts\activate
# Start the server
cd backend
python manage.py runserver
```
The API will be available at `http://127.0.0.1:8000/`.

### 2. Start the Frontend
The frontend runs on Node.js using Vite.
```bash
# Open a new terminal
cd MediBot\frontend
# Start the Vite dev server
npm run dev
```
The web application will be available at the URL provided by Vite (usually `http://localhost:5173/`).

## Feature Branching
We use standard Git flows:
1. Ensure you are on the `main` branch and pull latest changes: `git pull origin main`.
2. Create a new branch: `git checkout -b feature/your-feature-name`.
3. Follow the [[SDLC]] steps to implement your feature.
4. Commit your changes: `git commit -m "Add new feature"`.
5. Push your branch and open a Pull Request.

## Updating the Knowledge Base
If you edit files in the `knowledge_base/` folder:
1. Make sure to run the embedding script in the backend to update `chroma_db` and `faiss_indices`.
2. Test the bot's responses to ensure it's picking up the new data correctly.
