# Software Development Life Cycle (SDLC)

This document outlines the standard SDLC steps specifically tailored for the **MediBot** project, following an Agile-based iterative workflow.

## 1. Requirement Analysis (Planning)
- **Goal**: Understand the needs of the healthcare providers and patients using MediBot.
- **Tasks**:
  - Define what new medical features the AI agent should support.
  - Update the [[RAG_Knowledge_Base]] with new medical guidelines.
  - Identify regulatory constraints (e.g., HIPAA compliance).
- **Output**: Feature specifications, user stories.

## 2. System Design
- **Goal**: Architect the solution.
- **Tasks**:
  - Update the [[System_Architecture]] diagrams.
  - Define new API endpoints in the [[Backend_Overview]].
  - Map out the **ERD** (Entity-Relationship Diagram) for new SQLite models in [[Patients_App]] or [[Authentication_App]].
  - Design UI/UX mockups for the [[Frontend_Overview]].
- **Output**: ERD, Wireframes, API documentation.

## 3. Implementation (Coding)
- **Goal**: Build the features.
- **Tasks**:
  - **Frontend**: Develop React components using Tailwind CSS.
  - **Backend**: Implement Django models, views, and services.
  - **AI Integration**: Update `services.py` in the [[AI_Agent_App]] to incorporate new LLM prompts or vector searches.
- **Output**: Source code pushed to version control.

## 4. Testing
- **Goal**: Ensure quality and accuracy.
- **Tasks**:
  - **Unit Testing**: Run `tests.py` in Django apps.
  - **Integration Testing**: Verify the React frontend correctly calls the Django backend.
  - **AI Validation**: Test the RAG system to ensure hallucination-free and accurate medical responses using the knowledge base.
- **Output**: Test reports, bug fixes.

## 5. Deployment
- **Goal**: Release the feature to users.
- **Tasks**:
  - Build the frontend using `npm run build` (creates the `dist/` folder).
  - Collect static files and migrate the database in Django.
  - Deploy to the staging/production server.
- **Output**: Live application.

## 6. Maintenance & Feedback
- **Goal**: Keep the system reliable and up to date.
- **Tasks**:
  - Monitor logs (e.g., `debug.log`).
  - Periodically update the [[RAG_Knowledge_Base]] documents with the latest hospital policies.
  - Address user feedback.
- **Output**: Iteration backlog.
