# Fantasy Clips POC

A proof-of-concept application that helps fantasy football managers see their players' highlights without having to search through full games or highlight reels.

## Features

- **Sleeper API Integration**: Connect your Sleeper fantasy league
- **Automatic Highlight Detection**: Identifies touchdown plays, big gains, and other fantasy-relevant moments
- **YouTube Video Integration**: Finds and timestamps relevant video clips
- **Personalized Feed**: Shows only highlights for your rostered players
- **Mobile-First Design**: React Native app with modern UI

## Architecture

### Backend (Python/FastAPI)
- **Authentication**: JWT-based user authentication
- **Sleeper API Service**: Fetches league data, rosters, and player information
- **Highlight Service**: Processes play-by-play data to identify highlight-worthy plays
- **YouTube Service**: Searches and timestamps video clips
- **Database**: PostgreSQL for data persistence

### Frontend (React Native/Expo)
- **Authentication Screens**: Login and registration
- **League Connection**: Connect to Sleeper leagues
- **Highlights Feed**: Browse player highlights by week
- **Video Player**: Watch timestamped video clips
- **Player-Specific Views**: See highlights for individual players

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL
- Redis (optional, for background tasks)
- YouTube API key
- Sleeper account

### Backend Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp env.example .env
# Edit .env with your configuration
```

3. Set up the database:
```bash
# Create PostgreSQL database
createdb fantasy_clips

# Run migrations (tables will be created automatically)
python backend/main.py
```

4. Start the backend server:
```bash
cd backend
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

3. Run on your preferred platform:
```bash
npm run ios     # iOS simulator
npm run android # Android emulator
npm run web     # Web browser
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Create new account
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user

### Leagues
- `POST /api/leagues/connect` - Connect Sleeper league
- `GET /api/leagues/` - Get user's leagues
- `GET /api/leagues/{league_id}/roster/{week}` - Get roster for week
- `GET /api/leagues/{league_id}/players` - Get league players

### Highlights
- `POST /api/highlights/generate` - Generate highlights for week
- `GET /api/highlights/league/{league_id}/week/{week}` - Get highlights for league/week
- `GET /api/highlights/player/{player_id}/week/{week}` - Get player highlights

## Data Flow

1. **User connects Sleeper league** → League and roster data stored
2. **User requests highlights for week** → System fetches play-by-play data
3. **Highlight detection** → Identifies fantasy-relevant plays
4. **Video search** → Finds YouTube videos for each highlight
5. **Timestamp estimation** → Determines start/end times for clips
6. **User views highlights** → Personalized feed with embedded videos

## Key Services

### SleeperService
- Fetches league information, rosters, and player data
- Handles user authentication with Sleeper
- Manages league connections

### HighlightService
- Processes NFL play-by-play data
- Identifies highlight-worthy plays (touchdowns, big gains, etc.)
- Calculates fantasy points for plays

### YouTubeService
- Searches YouTube for relevant videos
- Ranks videos by relevance
- Estimates timestamps for specific plays

## Configuration

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string (optional)
- `SLEEPER_BASE_URL`: Sleeper API base URL
- `YOUTUBE_API_KEY`: YouTube Data API key
- `SECRET_KEY`: JWT secret key

### YouTube API Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable YouTube Data API v3
4. Create credentials (API key)
5. Add the API key to your `.env` file

## Limitations (POC)

- **Video Licensing**: Only embeds videos, doesn't store or redistribute
- **Timestamp Accuracy**: Uses heuristics for timestamp estimation
- **Real-time Updates**: Processes highlights after games complete
- **League Support**: Currently only supports Sleeper leagues

## Future Enhancements

- **Real-time Processing**: Live highlight detection during games
- **Multiple League Support**: ESPN, Yahoo Fantasy integration
- **Advanced Video AI**: Better timestamp detection using AI
- **Social Features**: Share highlights with league members
- **Push Notifications**: Alert users when highlights are ready
- **Analytics**: Track which players generate most highlights

## Legal Considerations

- **Video Rights**: Only embeds videos from authorized sources
- **API Terms**: Follows YouTube and Sleeper API terms of service
- **NFL Licensing**: For production use, consider NFL footage licensing

## Development Notes

This is a proof-of-concept application designed to demonstrate the core functionality. For production use, consider:

- Enhanced error handling and logging
- Rate limiting and API quotas
- Caching strategies for better performance
- Security improvements (HTTPS, input validation)
- Comprehensive testing suite
- Production database optimization
