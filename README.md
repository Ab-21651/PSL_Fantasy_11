# FastAPI Backend for Fantasy App

## Features
- FastAPI backend with async SQLAlchemy (asyncpg)
- Pydantic v2 for schemas
- JWT authentication (python-jose)
- Password hashing with bcrypt (passlib)
- Database URL from .env file (python-dotenv)
- CORS enabled for all origins
- Routers: players, fantasy, auth, ai (placeholder)
- PostgreSQL tables (already exist): players, career_stats, recent_form, users, fantasy_teams, fantasy_team_players, points_log

## Project Structure
- app/
  - main.py
  - db.py
  - models.py
  - schemas/
  - routers/
  - core/
- .env
- requirements.txt

## How to Run
1. Install dependencies: `pip install -r requirements.txt`
2. Set up your `.env` file with the correct `DATABASE_URL` and `SECRET_KEY`.
3. Run the server: `uvicorn app.main:app --reload`

---

This project is scaffolded for async, secure, and modern FastAPI development.
