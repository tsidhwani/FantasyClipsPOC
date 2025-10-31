from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    leagues = relationship("League", back_populates="user")

class League(Base):
    __tablename__ = "leagues"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    sleeper_league_id = Column(String, unique=True, index=True)
    name = Column(String)
    season = Column(String)
    scoring_settings = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="leagues")
    rosters = relationship("Roster", back_populates="league")

class Roster(Base):
    __tablename__ = "rosters"
    
    id = Column(Integer, primary_key=True, index=True)
    league_id = Column(Integer, ForeignKey("leagues.id"))
    week = Column(Integer)
    player_ids = Column(JSON)  # List of Sleeper player IDs
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    league = relationship("League", back_populates="rosters")

class Play(Base):
    __tablename__ = "plays"
    
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(String, index=True)
    play_id = Column(String, unique=True, index=True)
    week = Column(Integer, index=True)
    season = Column(String, index=True)
    quarter = Column(Integer)
    game_clock = Column(String)
    team = Column(String)
    player_ids = Column(JSON)  # List of player IDs involved
    event_type = Column(String)  # touchdown, reception, rush, etc.
    yards_gained = Column(Integer)
    fantasy_points = Column(Float)
    is_highlight_worthy = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    clips = relationship("Clip", back_populates="play")

class Clip(Base):
    __tablename__ = "clips"
    
    id = Column(Integer, primary_key=True, index=True)
    play_id = Column(Integer, ForeignKey("plays.id"))
    provider = Column(String)  # youtube, twitter, etc.
    url = Column(String)
    embed_url = Column(String)
    start_sec = Column(Integer)
    end_sec = Column(Integer)
    confidence = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    play = relationship("Play", back_populates="clips")
