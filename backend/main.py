from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
from dotenv import load_dotenv
import os

from database import get_db, engine, Base
from models import User, League, Roster, Play, Clip
from services.sleeper_service import SleeperService
from services.highlight_service import HighlightService
from services.youtube_service import YouTubeService
from routers import auth, leagues, highlights

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fantasy Clips POC", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(leagues.router, prefix="/api/leagues", tags=["leagues"])
app.include_router(highlights.router, prefix="/api/highlights", tags=["highlights"])

@app.get("/")
async def root():
    return {"message": "Fantasy Clips POC API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
