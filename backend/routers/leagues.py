from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from pydantic import BaseModel
from datetime import datetime

from database import get_db
from models import User, League, Roster
from services.sleeper_service import SleeperService
from routers.auth import get_current_user

router = APIRouter()

class LeagueConnect(BaseModel):
    sleeper_username: str
    league_id: str

class LeagueResponse(BaseModel):
    id: int
    sleeper_league_id: str
    name: str
    season: str
    scoring_settings: Dict
    
    class Config:
        from_attributes = True

class RosterResponse(BaseModel):
    id: int
    week: int
    player_ids: List[str]
    
    class Config:
        from_attributes = True

@router.post("/connect", response_model=LeagueResponse)
async def connect_league(
    league_data: LeagueConnect,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Connect a Sleeper league to the user's account"""
    sleeper_service = SleeperService()
    
    try:
        # Get league info from Sleeper
        league_info = await sleeper_service.get_league_info(league_data.league_id)
        if not league_info:
            raise HTTPException(status_code=404, detail="League not found")
        
        # Check if league already exists for this user
        existing_league = db.query(League).filter(
            League.user_id == current_user.id,
            League.sleeper_league_id == league_data.league_id
        ).first()
        
        if existing_league:
            return existing_league
        
        # Create new league record
        league = League(
            user_id=current_user.id,
            sleeper_league_id=league_data.league_id,
            name=league_info.get('name', 'Unknown League'),
            season=league_info.get('season', '2024'),
            scoring_settings=league_info.get('scoring_settings', {})
        )
        
        db.add(league)
        db.commit()
        db.refresh(league)
        
        await sleeper_service.close()
        return league
        
    except Exception as e:
        await sleeper_service.close()
        raise HTTPException(status_code=500, detail=f"Error connecting league: {str(e)}")

@router.get("/", response_model=List[LeagueResponse])
async def get_user_leagues(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all leagues for the current user"""
    leagues = db.query(League).filter(League.user_id == current_user.id).all()
    return leagues

@router.get("/{league_id}/roster/{week}", response_model=RosterResponse)
async def get_roster_for_week(
    league_id: int,
    week: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get roster for a specific league and week"""
    # Verify league belongs to user
    league = db.query(League).filter(
        League.id == league_id,
        League.user_id == current_user.id
    ).first()
    
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    
    # Check if roster already exists
    existing_roster = db.query(Roster).filter(
        Roster.league_id == league_id,
        Roster.week == week
    ).first()
    
    if existing_roster:
        return existing_roster
    
    # Fetch roster from Sleeper
    sleeper_service = SleeperService()
    
    try:
        # Get league users to find current user's roster
        league_users = await sleeper_service.get_league_users(league.sleeper_league_id)
        user_mapping = {user['user_id']: user for user in league_users}
        
        # Get rosters
        rosters = await sleeper_service.get_league_rosters(league.sleeper_league_id)
        
        # Find user's roster
        user_roster = None
        for roster in rosters:
            if roster.get('owner_id') in user_mapping:
                user_roster = roster
                break
        
        if not user_roster:
            raise HTTPException(status_code=404, detail="Roster not found")
        
        # Create roster record
        roster = Roster(
            league_id=league_id,
            week=week,
            player_ids=user_roster.get('players', [])
        )
        
        db.add(roster)
        db.commit()
        db.refresh(roster)
        
        await sleeper_service.close()
        return roster
        
    except Exception as e:
        await sleeper_service.close()
        raise HTTPException(status_code=500, detail=f"Error fetching roster: {str(e)}")

@router.get("/{league_id}/players")
async def get_league_players(
    league_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all players in a league with their details"""
    # Verify league belongs to user
    league = db.query(League).filter(
        League.id == league_id,
        League.user_id == current_user.id
    ).first()
    
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    
    sleeper_service = SleeperService()
    
    try:
        # Get all players
        players = await sleeper_service.get_players()
        
        # Get league rosters to see which players are rostered
        rosters = await sleeper_service.get_league_rosters(league.sleeper_league_id)
        all_rostered_players = set()
        for roster in rosters:
            all_rostered_players.update(roster.get('players', []))
        
        # Filter and format player data
        league_players = []
        for player_id, player_data in players.items():
            if player_id in all_rostered_players:
                league_players.append({
                    'player_id': player_id,
                    'name': player_data.get('full_name', 'Unknown'),
                    'position': player_data.get('position', 'Unknown'),
                    'team': player_data.get('team', 'Unknown'),
                    'status': player_data.get('status', 'Unknown')
                })
        
        await sleeper_service.close()
        return league_players
        
    except Exception as e:
        await sleeper_service.close()
        raise HTTPException(status_code=500, detail=f"Error fetching players: {str(e)}")
