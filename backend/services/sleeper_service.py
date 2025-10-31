import httpx
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class SleeperService:
    def __init__(self):
        self.base_url = os.getenv("SLEEPER_BASE_URL", "https://api.sleeper.app/v1")
        self.client = httpx.AsyncClient()
    
    async def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        try:
            response = await self.client.get(f"{self.base_url}/user/{username}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error fetching user: {e}")
            return None
    
    async def get_user_leagues(self, user_id: str, season: str = "2024") -> List[Dict]:
        """Get all leagues for a user"""
        try:
            response = await self.client.get(f"{self.base_url}/user/{user_id}/leagues/nfl/{season}")
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Error fetching leagues: {e}")
            return []
    
    async def get_league_rosters(self, league_id: str) -> List[Dict]:
        """Get all rosters for a league"""
        try:
            response = await self.client.get(f"{self.base_url}/league/{league_id}/rosters")
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Error fetching rosters: {e}")
            return []
    
    async def get_league_users(self, league_id: str) -> List[Dict]:
        """Get all users in a league"""
        try:
            response = await self.client.get(f"{self.base_url}/league/{league_id}/users")
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Error fetching league users: {e}")
            return []
    
    async def get_league_matchups(self, league_id: str, week: int) -> List[Dict]:
        """Get matchups for a specific week"""
        try:
            response = await self.client.get(f"{self.base_url}/league/{league_id}/matchups/{week}")
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Error fetching matchups: {e}")
            return []
    
    async def get_players(self) -> Dict:
        """Get all NFL players"""
        try:
            response = await self.client.get(f"{self.base_url}/players/nfl")
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            print(f"Error fetching players: {e}")
            return {}
    
    async def get_player_stats(self, player_id: str, season: str = "2024", week: int = None) -> Dict:
        """Get player stats for a season/week"""
        try:
            if week:
                url = f"{self.base_url}/players/nfl/stats/{player_id}/{season}/{week}"
            else:
                url = f"{self.base_url}/players/nfl/stats/{player_id}/{season}"
            
            response = await self.client.get(url)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            print(f"Error fetching player stats: {e}")
            return {}
    
    async def get_roster_for_user(self, league_id: str, user_id: str) -> Optional[Dict]:
        """Get roster for a specific user in a league"""
        try:
            rosters = await self.get_league_rosters(league_id)
            for roster in rosters:
                if roster.get("owner_id") == user_id:
                    return roster
            return None
        except Exception as e:
            print(f"Error fetching user roster: {e}")
            return None
    
    async def get_league_info(self, league_id: str) -> Optional[Dict]:
        """Get league information"""
        try:
            response = await self.client.get(f"{self.base_url}/league/{league_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error fetching league info: {e}")
            return None
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
