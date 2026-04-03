from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import players, fantasy, auth, ai, matches, results
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="CricMind API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(players.router,  prefix="/players",  tags=["players"])
app.include_router(fantasy.router,  prefix="/fantasy",  tags=["fantasy"])
app.include_router(auth.router,     prefix="/auth",     tags=["auth"])
app.include_router(ai.router,       prefix="/ai",       tags=["ai"])
app.include_router(matches.router,  prefix="/matches",  tags=["matches"])
app.include_router(results.router,  prefix="/results",  tags=["results"])

@app.get("/")
def root():
    return {"message": "CricMind API is running", "version": "1.0.0"}