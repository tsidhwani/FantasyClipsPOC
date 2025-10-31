from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class YouTubeService:
    def __init__(self):
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError("YouTube API key not found in environment variables")
        
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
    
    def build_search_query(self, player_name: str, play_description: str, week: int, 
                          home_team: str, away_team: str) -> str:
        """Build a search query for YouTube"""
        # Clean up player name (remove common suffixes)
        clean_name = player_name.replace(" Jr.", "").replace(" Sr.", "").replace(" III", "").replace(" II", "")
        
        # Build query based on play type
        if "touchdown" in play_description.lower():
            query = f"{clean_name} touchdown Week {week} {away_team} at {home_team}"
        elif "reception" in play_description.lower():
            query = f"{clean_name} catch Week {week} {away_team} at {home_team}"
        elif "rush" in play_description.lower():
            query = f"{clean_name} run Week {week} {away_team} at {home_team}"
        else:
            query = f"{clean_name} Week {week} {away_team} at {home_team}"
        
        return query
    
    def search_videos(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search for videos on YouTube"""
        try:
            # Search for videos
            search_response = self.youtube.search().list(
                q=query,
                part='id,snippet',
                maxResults=max_results,
                type='video',
                order='relevance',
                publishedAfter='2024-01-01T00:00:00Z'  # Only recent videos
            ).execute()
            
            videos = []
            for search_result in search_response.get('items', []):
                video_id = search_result['id']['videoId']
                snippet = search_result['snippet']
                
                # Get video details
                video_response = self.youtube.videos().list(
                    part='contentDetails,statistics',
                    id=video_id
                ).execute()
                
                if video_response['items']:
                    video_details = video_response['items'][0]
                    videos.append({
                        'video_id': video_id,
                        'title': snippet['title'],
                        'description': snippet['description'],
                        'channel_title': snippet['channelTitle'],
                        'published_at': snippet['publishedAt'],
                        'duration': video_details['contentDetails']['duration'],
                        'view_count': video_details['statistics'].get('viewCount', 0),
                        'url': f"https://www.youtube.com/watch?v={video_id}",
                        'embed_url': f"https://www.youtube.com/embed/{video_id}"
                    })
            
            return videos
            
        except HttpError as e:
            print(f"Error searching YouTube: {e}")
            return []
    
    def rank_videos(self, videos: List[Dict], play_data: Dict) -> List[Dict]:
        """Rank videos by relevance to the play"""
        for video in videos:
            score = 0
            
            # Channel preference (NFL, team channels get higher scores)
            channel_title = video['channel_title'].lower()
            if 'nfl' in channel_title:
                score += 10
            elif any(team in channel_title for team in ['chiefs', 'bills', 'patriots', 'dolphins']):
                score += 5
            
            # Title relevance
            title = video['title'].lower()
            play_type = play_data.get('play_type', '').lower()
            
            if 'touchdown' in play_type and 'touchdown' in title:
                score += 8
            elif 'reception' in play_type and ('catch' in title or 'reception' in title):
                score += 6
            elif 'rush' in play_type and ('run' in title or 'rush' in title):
                score += 6
            
            # Player name in title
            player_name = play_data.get('player_name', '').lower()
            if player_name and player_name in title:
                score += 5
            
            # Week mentioned
            week = play_data.get('week')
            if week and f'week {week}' in title:
                score += 3
            
            # View count (popularity)
            view_count = int(video.get('view_count', 0))
            if view_count > 100000:
                score += 2
            elif view_count > 10000:
                score += 1
            
            video['relevance_score'] = score
        
        # Sort by relevance score
        return sorted(videos, key=lambda x: x['relevance_score'], reverse=True)
    
    def estimate_timestamp(self, video: Dict, play_data: Dict) -> Optional[int]:
        """Estimate the timestamp for a specific play in a video"""
        try:
            # Get video chapters if available
            video_id = video['video_id']
            video_response = self.youtube.videos().list(
                part='snippet',
                id=video_id
            ).execute()
            
            if not video_response['items']:
                return None
            
            description = video_response['items'][0]['snippet']['description']
            
            # Look for chapter markers in description
            lines = description.split('\n')
            for line in lines:
                if ':' in line and any(keyword in line.lower() for keyword in ['touchdown', 'td', 'score']):
                    # Try to parse timestamp from chapter
                    try:
                        time_part = line.split(':')[0].strip()
                        if ':' in time_part:
                            minutes, seconds = map(int, time_part.split(':'))
                            return minutes * 60 + seconds
                    except:
                        continue
            
            # Fallback: estimate based on game flow
            quarter = play_data.get('quarter', 1)
            game_clock = play_data.get('game_clock', 900)  # Default to 15 minutes
            
            # Rough estimation: each quarter is about 3-4 minutes in highlights
            base_time = (quarter - 1) * 240  # 4 minutes per quarter
            
            # Adjust based on game clock (later in quarter = later in video)
            if isinstance(game_clock, (int, float)):
                clock_factor = (900 - game_clock) / 900  # 0 to 1
                adjustment = clock_factor * 60  # Up to 1 minute adjustment
                base_time += adjustment
            
            return int(base_time)
            
        except Exception as e:
            print(f"Error estimating timestamp: {e}")
            return None
    
    def find_best_clip(self, play_data: Dict, player_name: str, 
                      home_team: str, away_team: str) -> Optional[Dict]:
        """Find the best video clip for a play"""
        try:
            # Build search query
            query = self.build_search_query(
                player_name, 
                play_data.get('description', ''),
                play_data.get('week', 1),
                home_team,
                away_team
            )
            
            # Search for videos
            videos = self.search_videos(query, max_results=10)
            
            if not videos:
                return None
            
            # Rank videos by relevance
            ranked_videos = self.rank_videos(videos, play_data)
            
            if not ranked_videos:
                return None
            
            # Get the best video
            best_video = ranked_videos[0]
            
            # Estimate timestamp
            start_sec = self.estimate_timestamp(best_video, play_data)
            
            return {
                'provider': 'youtube',
                'url': best_video['url'],
                'embed_url': best_video['embed_url'],
                'start_sec': start_sec,
                'end_sec': start_sec + 30 if start_sec else None,  # 30 second clip
                'confidence': min(best_video['relevance_score'] / 20, 1.0),  # Normalize to 0-1
                'title': best_video['title'],
                'channel': best_video['channel_title']
            }
            
        except Exception as e:
            print(f"Error finding best clip: {e}")
            return None
