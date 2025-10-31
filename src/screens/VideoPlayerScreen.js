import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  Dimensions,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import YouTube from 'react-native-youtube-iframe';

const { width, height } = Dimensions.get('window');

export default function VideoPlayerScreen({ navigation, route }) {
  const { highlight, clip } = route.params;
  const [playing, setPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);

  const handlePlayPause = () => {
    setPlaying(!playing);
  };

  const handleSeekTo = (time) => {
    // YouTube player will handle seeking
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getVideoId = (url) => {
    const match = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/);
    return match ? match[1] : null;
  };

  const videoId = getVideoId(clip.url);

  if (!videoId) {
    return (
      <LinearGradient colors={['#1a1a1a', '#2d2d2d']} style={styles.container}>
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>Invalid video URL</Text>
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => navigation.goBack()}
          >
            <Text style={styles.backButtonText}>Go Back</Text>
          </TouchableOpacity>
        </View>
      </LinearGradient>
    );
  }

  return (
    <LinearGradient colors={['#1a1a1a', '#2d2d2d']} style={styles.container}>
      <View style={styles.content}>
        <View style={styles.videoContainer}>
          <YouTube
            videoId={videoId}
            play={playing}
            onChangeState={(state) => {
              if (state === 'ended') {
                setPlaying(false);
              }
            }}
            onProgress={(data) => {
              setCurrentTime(data.currentTime);
            }}
            onDuration={(data) => {
              setDuration(data.duration);
            }}
            style={styles.youtubePlayer}
            initialPlayerParams={{
              start: clip.start_sec || 0,
              end: clip.end_sec || clip.start_sec + 30,
            }}
          />
        </View>

        <View style={styles.highlightInfo}>
          <Text style={styles.eventType}>{highlight.event_type}</Text>
          <Text style={styles.yardsGained}>
            {highlight.yards_gained > 0 ? `+${highlight.yards_gained} yards` : `${highlight.yards_gained} yards`}
          </Text>
          <Text style={styles.fantasyPoints}>+{highlight.fantasy_points.toFixed(1)} fantasy points</Text>
          <Text style={styles.gameInfo}>
            Week {highlight.week} • Q{highlight.quarter} • {highlight.game_clock}s remaining
          </Text>
        </View>

        <View style={styles.controls}>
          <TouchableOpacity
            style={styles.controlButton}
            onPress={handlePlayPause}
          >
            <Text style={styles.controlButtonText}>
              {playing ? '⏸️' : '▶️'}
            </Text>
          </TouchableOpacity>

          <View style={styles.timeInfo}>
            <Text style={styles.timeText}>
              {formatTime(currentTime)} / {formatTime(duration)}
            </Text>
          </View>

          <TouchableOpacity
            style={styles.controlButton}
            onPress={() => {
              // Seek to start of highlight
              handleSeekTo(clip.start_sec || 0);
            }}
          >
            <Text style={styles.controlButtonText}>⏮️</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.actions}>
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => {
              // Share functionality would go here
              Alert.alert('Share', 'Share functionality coming soon!');
            }}
          >
            <Text style={styles.actionButtonText}>Share</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => navigation.goBack()}
          >
            <Text style={styles.actionButtonText}>Back to Highlights</Text>
          </TouchableOpacity>
        </View>
      </View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
    paddingTop: 20,
  },
  videoContainer: {
    borderRadius: 10,
    overflow: 'hidden',
    marginBottom: 20,
  },
  youtubePlayer: {
    width: width - 40,
    height: (width - 40) * 9 / 16, // 16:9 aspect ratio
  },
  highlightInfo: {
    backgroundColor: '#333',
    borderRadius: 10,
    padding: 15,
    marginBottom: 20,
  },
  eventType: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    textTransform: 'capitalize',
    marginBottom: 5,
  },
  yardsGained: {
    color: '#4CAF50',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  fantasyPoints: {
    color: '#FFD700',
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  gameInfo: {
    color: '#ccc',
    fontSize: 12,
  },
  controls: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 20,
  },
  controlButton: {
    backgroundColor: '#333',
    borderRadius: 25,
    width: 50,
    height: 50,
    alignItems: 'center',
    justifyContent: 'center',
    marginHorizontal: 10,
  },
  controlButtonText: {
    color: '#fff',
    fontSize: 20,
  },
  timeInfo: {
    marginHorizontal: 20,
  },
  timeText: {
    color: '#fff',
    fontSize: 14,
  },
  actions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  actionButton: {
    backgroundColor: '#007AFF',
    borderRadius: 10,
    paddingVertical: 12,
    paddingHorizontal: 20,
    flex: 0.45,
    alignItems: 'center',
  },
  actionButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorText: {
    color: '#fff',
    fontSize: 18,
    marginBottom: 20,
  },
  backButton: {
    backgroundColor: '#007AFF',
    borderRadius: 10,
    paddingVertical: 12,
    paddingHorizontal: 20,
  },
  backButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
