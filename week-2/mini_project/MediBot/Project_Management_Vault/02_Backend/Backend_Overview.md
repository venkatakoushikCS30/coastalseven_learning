# Backend Overview

The MediBot backend is built using the **Django** Python web framework. It serves as the API gateway and central logic processor for the entire system.

## Core Structure
The main entry point and configuration are located in `backend/backend/` (containing `settings.py`, `urls.py`). 
The database used is `db.sqlite3`.

## Installed Apps
The backend is modularized into several Django apps:
- **[[AI_Agent_App]]**: Handles all RAG and LLM integrations.
- **[[Authentication_App]]**: Manages user sign-ups, logins, and permissions.
- **[[Patients_App]]**: Manages medical profiles and records.

## Key Files
- `manage.py`: The command-line utility for Django tasks (running server, migrations).
- `seed_data.py`: A script used to insert mock/dummy data into the database for testing.
- `debug.log`: File containing application logs and errors.

## Running the Backend
To run the server locally:
```bash
cd backend
source ../venv/Scripts/activate # Or venv/bin/activate on Mac/Linux
python manage.py runserver
```
