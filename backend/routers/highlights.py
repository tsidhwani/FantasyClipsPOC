from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime

from database import get_db
from models import User, League, Play, Clip
from services.sleeper_service import SleeperService
from services.highlight_service import HighlightService
from services.youtube_service import YouTubeService
from routers.auth import get_current_user

router = APIRouter()

class HighlightResponse(BaseModel):
    id: int
    game_id: str
    play_id: str
    week: int
    quarter: int
    game_clock: str
    team: str
    player_ids: List[str]
    event_type: str
    yards_gained: int
    fantasy_points: float
    is_highlight_worthy: bool
    clips: List[Dict]
    
    class Config:
        from_attributes = True

class GenerateHighlightsRequest(BaseModel):
    league_id: int
    week: int
    season: int = 2024

@router.post("/generate")
async def generate_highlights(
    request: GenerateHighlightsRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate highlights for a specific league and week"""
    # Verify league belongs to user
    league = db.query(League).filter(
        League.id == request.league_id,
        League.user_id == current_user.id
    ).first()
    
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    
    # Get roster for the week
    from models import Roster
    roster = db.query(Roster).filter(
        Roster.league_id == request.league_id,
        Roster.week == request.week
    ).first()
    
    if not roster:
        raise HTTPException(status_code=404, detail="Roster not found for this week")
    
    # Start background task to process highlights
    background_tasks.add_task(
        process_highlights_background,
        league_id=request.league_id,
        week=request.week,
        season=request.season,
        roster_id=roster.id
    )
    
    return {"message": "Highlight generation started", "status": "processing"}

async def process_highlights_background(
    league_id: int,
    week: int,
    season: int,
    roster_id: int
):
    """Background task to process highlights"""
    from database import SessionLocal
    from services.sleeper_service import SleeperService
    
    db = SessionLocal()
    try:
        # Get roster
        from models import Roster
        roster = db.query(Roster).filter(Roster.id == roster_id).first()
        if not roster:
            return
        
        # Process highlights
        highlight_service = HighlightService(db)
        highlights = await highlight_service.process_roster_highlights(roster, season, week)
        
        # Save highlights to database
        saved_plays = await highlight_service.save_highlights_to_db(highlights)
        
        # Find video clips for each highlight
        youtube_service = YouTubeService()
        sleeper_service = SleeperService()
        
        # Get players data for names
        players = await sleeper_service.get_players()
        
        for play in saved_plays:
            if play.is_highlight_worthy:
                # Get player name (simplified - in production, you'd want better player matching)
                player_id = play.player_ids[0] if play.player_ids else None
                player_name = "Unknown Player"
                
                if player_id and player_id in players:
                    player_data = players[player_id]
                    player_name = player_data.get('full_name', 'Unknown Player')
                
                # Find video clip
                clip_data = youtube_service.find_best_clip(
                    {
                        'description': f"{play.event_type} {play.yards_gained} yards",
                        'week': play.week,
                        'quarter': play.quarter,
                        'game_clock': play.game_clock
                    },
                    player_name,
                    play.team,  # Simplified - you'd want actual home/away teams
                    "Opponent"  # Simplified
                )
                
                if clip_data:
                    # Save clip to database
                    clip = Clip(
                        play_id=play.id,
                        provider=clip_data['provider'],
                        url=clip_data['url'],
                        embed_url=clip_data['embed_url'],
                        start_sec=clip_data['start_sec'],
                        end_sec=clip_data['end_sec'],
                        confidence=clip_data['confidence']
                    )
                    db.add(clip)
        
        db.commit()
        
    except Exception as e:
        print(f"Error processing highlights: {e}")
        db.rollback()
    finally:
        db.close()

@router.get("/league/{league_id}/week/{week}", response_model=List[HighlightResponse])
async def get_highlights_for_week(
    league_id: int,
    week: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get highlights for a specific league and week"""
    # Verify league belongs to user
    league = db.query(League).filter(
        League.id == league_id,
        League.user_id == current_user.id
    ).first()
    
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    
    # Get highlights for the week
    highlights = db.query(Play).filter(
        Play.week == week,
        Play.is_highlight_worthy == True
    ).all()
    
    # Get clips for each highlight
    result = []
    for highlight in highlights:
        clips = db.query(Clip).filter(Clip.play_id == highlight.id).all()
        clip_data = [
            {
                'id': clip.id,
                'provider': clip.provider,
                'url': clip.url,
                'embed_url': clip.embed_url,
                'start_sec': clip.start_sec,
                'end_sec': clip.end_sec,
                'confidence': clip.confidence
            }
            for clip in clips
        ]
        
        result.append({
            'id': highlight.id,
            'game_id': highlight.game_id,
            'play_id': highlight.play_id,
            'week': highlight.week,
            'quarter': highlight.quarter,
            'game_clock': highlight.game_clock,
            'team': highlight.team,
            'player_ids': highlight.player_ids,
            'event_type': highlight.event_type,
            'yards_gained': highlight.yards_gained,
            'fantasy_points': highlight.fantasy_points,
            'is_highlight_worthy': highlight.is_highlight_worthy,
            'clips': clip_data
        })
    
    return result

@router.get("/player/{player_id}/week/{week}")
async def get_player_highlights(
    player_id: str,
    week: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get highlights for a specific player and week"""
    # Get highlights for the player
    highlights = db.query(Play).filter(
        Play.week == week,
        Play.player_ids.contains([player_id]),
        Play.is_highlight_worthy == True
    ).all()
    
    result = []
    for highlight in highlights:
        clips = db.query(Clip).filter(Clip.play_id == highlight.id).all()
        clip_data = [
            {
                'id': clip.id,
                'provider': clip.provider,
                'url': clip.url,
                'embed_url': clip.embed_url,
                'start_sec': clip.start_sec,
                'end_sec': clip.end_sec,
                'confidence': clip.confidence
            }
            for clip in clips
        ]
        
        result.append({
            'id': highlight.id,
            'game_id': highlight.game_id,
            'play_id': highlight.play_id,
            'week': highlight.week,
            'quarter': highlight.quarter,
            'game_clock': highlight.game_clock,
            'team': highlight.team,
            'player_ids': highlight.player_ids,
            'event_type': highlight.event_type,
            'yards_gained': highlight.yards_gained,
            'fantasy_points': highlight.fantasy_points,
            'is_highlight_worthy': highlight.is_highlight_worthy,
            'clips': clip_data
        })
    
    return result
