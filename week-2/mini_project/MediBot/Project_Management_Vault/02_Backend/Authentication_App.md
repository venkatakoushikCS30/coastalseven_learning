# Authentication App

The `authentication` app handles user identity for MediBot.

## Responsibilities
- User Registration (Sign up)
- User Authentication (Login / JWT Tokens or Session Auth)
- Password Management
- Role-based Access Control (e.g., distinguishing between a Doctor and a Patient).

## Key Files
- `models.py`: Contains the custom User model if extended from Django's default `AbstractUser`.
- `views.py`: Exposes API endpoints like `/api/auth/login/` and `/api/auth/register/`.
