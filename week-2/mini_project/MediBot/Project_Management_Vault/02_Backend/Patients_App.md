# Patients App

The `patients` app manages the core medical data entities in the MediBot system.

## Responsibilities
- Storing patient demographic information.
- Managing patient medical history.
- Linking patients to their respective authenticated user accounts (managed by [[Authentication_App]]).

## Key Files
- `models.py`: Defines the `Patient` ERD schema (Entity-Relationship Diagram), including fields like age, medical conditions, and linked user IDs.
- `views.py`: Exposes CRUD (Create, Read, Update, Delete) endpoints for patient records (e.g., `/api/patients/`).
