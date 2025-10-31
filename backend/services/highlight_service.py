import nfl_data_py as nfl
import pandas as pd
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from models import Play, Roster
import asyncio

class HighlightService:
    def __init__(self, db: Session):
        self.db = db
    
    def is_highlight_worthy(self, play_data: Dict) -> bool:
        """Determine if a play is highlight-worthy based on fantasy relevance"""
        event_type = play_data.get('play_type', '')
        yards_gained = play_data.get('yards_gained', 0)
        
        # Touchdowns are always highlight-worthy
        if 'touchdown' in event_type.lower():
            return True
        
        # Big plays (20+ yards)
        if yards_gained and yards_gained >= 20:
            return True
        
        # Interceptions and fumbles
        if event_type in ['pass_interception', 'fumble']:
            return True
        
        # Sacks
        if event_type == 'pass_sack':
            return True
        
        # Field goals (40+ yards)
        if event_type == 'field_goal' and yards_gained and yards_gained >= 40:
            return True
        
        return False
    
    def calculate_fantasy_points(self, play_data: Dict, scoring_settings: Dict = None) -> float:
        """Calculate fantasy points for a play"""
        if not scoring_settings:
            # Default PPR scoring
            scoring_settings = {
                'pass_td': 4,
                'rush_td': 6,
                'rec_td': 6,
                'pass_yd': 0.04,
                'rush_yd': 0.1,
                'rec_yd': 0.1,
                'rec': 1,
                'int': -2,
                'fumble_lost': -2
            }
        
        points = 0.0
        event_type = play_data.get('play_type', '')
        yards_gained = play_data.get('yards_gained', 0)
        
        # Touchdown points
        if 'pass_touchdown' in event_type:
            points += scoring_settings.get('pass_td', 4)
        elif 'rush_touchdown' in event_type:
            points += scoring_settings.get('rush_td', 6)
        elif 'receiving_touchdown' in event_type:
            points += scoring_settings.get('rec_td', 6)
        
        # Yardage points
        if 'pass' in event_type and yards_gained:
            points += yards_gained * scoring_settings.get('pass_yd', 0.04)
        elif 'rush' in event_type and yards_gained:
            points += yards_gained * scoring_settings.get('rush_yd', 0.1)
        elif 'receiving' in event_type and yards_gained:
            points += yards_gained * scoring_settings.get('rec_yd', 0.1)
        
        # Reception points (PPR)
        if 'reception' in event_type:
            points += scoring_settings.get('rec', 1)
        
        # Negative points
        if 'interception' in event_type:
            points += scoring_settings.get('int', -2)
        elif 'fumble' in event_type:
            points += scoring_settings.get('fumble_lost', -2)
        
        return points
    
    async def fetch_weekly_plays(self, season: int, week: int) -> pd.DataFrame:
        """Fetch play-by-play data for a specific week"""
        try:
            # Fetch play-by-play data
            pbp = nfl.import_pbp_data([season], downcast=True, cache=True, alt_path=None)
            
            # Filter for the specific week
            weekly_pbp = pbp[pbp['week'] == week].copy()
            
            return weekly_pbp
        except Exception as e:
            print(f"Error fetching weekly plays: {e}")
            return pd.DataFrame()
    
    async def process_roster_highlights(self, roster: Roster, season: int, week: int) -> List[Dict]:
        """Process highlights for a specific roster"""
        try:
            # Fetch weekly plays
            weekly_pbp = await self.fetch_weekly_plays(season, week)
            
            if weekly_pbp.empty:
                return []
            
            highlights = []
            player_ids = roster.player_ids or []
            
            # Filter plays for roster players
            for _, play in weekly_pbp.iterrows():
                # Check if any roster player is involved
                involved_players = []
                for player_id in player_ids:
                    if (play.get('passer_player_id') == player_id or 
                        play.get('rusher_player_id') == player_id or
                        play.get('receiver_player_id') == player_id):
                        involved_players.append(player_id)
                
                if involved_players:
                    play_data = {
                        'game_id': play.get('game_id'),
                        'play_id': play.get('play_id'),
                        'week': week,
                        'season': str(season),
                        'quarter': play.get('qtr'),
                        'game_clock': play.get('game_seconds_remaining'),
                        'team': play.get('posteam'),
                        'player_ids': involved_players,
                        'play_type': play.get('play_type'),
                        'yards_gained': play.get('yards_gained', 0),
                        'description': play.get('desc', ''),
                        'fantasy_points': self.calculate_fantasy_points(play.to_dict())
                    }
                    
                    if self.is_highlight_worthy(play_data):
                        play_data['is_highlight_worthy'] = True
                        highlights.append(play_data)
            
            return highlights
            
        except Exception as e:
            print(f"Error processing roster highlights: {e}")
            return []
    
    async def save_highlights_to_db(self, highlights: List[Dict]) -> List[Play]:
        """Save highlights to database"""
        saved_plays = []
        
        for highlight in highlights:
            # Check if play already exists
            existing_play = self.db.query(Play).filter(
                Play.play_id == highlight['play_id']
            ).first()
            
            if not existing_play:
                play = Play(
                    game_id=highlight['game_id'],
                    play_id=highlight['play_id'],
                    week=highlight['week'],
                    season=highlight['season'],
                    quarter=highlight['quarter'],
                    game_clock=str(highlight['game_clock']),
                    team=highlight['team'],
                    player_ids=highlight['player_ids'],
                    event_type=highlight['play_type'],
                    yards_gained=highlight['yards_gained'],
                    fantasy_points=highlight['fantasy_points'],
                    is_highlight_worthy=highlight.get('is_highlight_worthy', False)
                )
                
                self.db.add(play)
                saved_plays.append(play)
        
        self.db.commit()
        return saved_plays
