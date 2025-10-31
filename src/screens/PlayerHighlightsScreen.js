import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  FlatList,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { highlightsAPI } from '../services/api';

export default function PlayerHighlightsScreen({ navigation, route }) {
  const { playerId, playerName, week } = route.params;
  const [highlights, setHighlights] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPlayerHighlights();
  }, [playerId, week]);

  const loadPlayerHighlights = async () => {
    setLoading(true);
    try {
      const response = await highlightsAPI.getPlayerHighlights(playerId, week);
      setHighlights(response.data);
    } catch (error) {
      console.error('Error loading player highlights:', error);
      Alert.alert('Error', 'Failed to load player highlights');
    } finally {
      setLoading(false);
    }
  };

  const handlePlayHighlight = (highlight) => {
    if (highlight.clips && highlight.clips.length > 0) {
      navigation.navigate('VideoPlayer', { 
        highlight,
        clip: highlight.clips[0]
      });
    } else {
      Alert.alert('No Video', 'No video clip available for this highlight');
    }
  };

  const renderHighlightItem = ({ item }) => (
    <TouchableOpacity
      style={styles.highlightItem}
      onPress={() => handlePlayHighlight(item)}
    >
      <View style={styles.highlightHeader}>
        <Text style={styles.eventType}>{item.event_type}</Text>
        <Text style={styles.fantasyPoints}>+{item.fantasy_points.toFixed(1)} pts</Text>
      </View>
      
      <Text style={styles.yardsGained}>
        {item.yards_gained > 0 ? `+${item.yards_gained} yards` : `${item.yards_gained} yards`}
      </Text>
      
      <Text style={styles.gameInfo}>
        Q{item.quarter} • {item.game_clock}s remaining
      </Text>
      
      {item.clips && item.clips.length > 0 && (
        <View style={styles.videoIndicator}>
          <Text style={styles.videoText}>📹 Video Available</Text>
        </View>
      )}
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <LinearGradient colors={['#1a1a1a', '#2d2d2d']} style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.loadingText}>Loading highlights...</Text>
        </View>
      </LinearGradient>
    );
  }

  return (
    <LinearGradient colors={['#1a1a1a', '#2d2d2d']} style={styles.container}>
      <View style={styles.content}>
        <View style={styles.playerHeader}>
          <Text style={styles.playerName}>{playerName}</Text>
          <Text style={styles.weekText}>Week {week}</Text>
        </View>

        <FlatList
          data={highlights}
          renderItem={renderHighlightItem}
          keyExtractor={(item) => item.id.toString()}
          style={styles.highlightsList}
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Text style={styles.emptyText}>No highlights found for {playerName}</Text>
              <Text style={styles.emptySubtext}>
                This player didn't have any highlight-worthy plays this week
              </Text>
            </View>
          }
        />
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
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    color: '#fff',
    fontSize: 16,
    marginTop: 10,
  },
  playerHeader: {
    backgroundColor: '#333',
    borderRadius: 10,
    padding: 20,
    marginBottom: 20,
    alignItems: 'center',
  },
  playerName: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  weekText: {
    color: '#ccc',
    fontSize: 16,
  },
  highlightsList: {
    flex: 1,
  },
  highlightItem: {
    backgroundColor: '#333',
    borderRadius: 10,
    padding: 15,
    marginBottom: 10,
  },
  highlightHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 5,
  },
  eventType: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    textTransform: 'capitalize',
  },
  fantasyPoints: {
    color: '#4CAF50',
    fontSize: 14,
    fontWeight: 'bold',
  },
  yardsGained: {
    color: '#ccc',
    fontSize: 14,
    marginBottom: 5,
  },
  gameInfo: {
    color: '#666',
    fontSize: 12,
    marginBottom: 5,
  },
  videoIndicator: {
    alignSelf: 'flex-start',
    backgroundColor: '#007AFF',
    borderRadius: 5,
    paddingHorizontal: 8,
    paddingVertical: 4,
  },
  videoText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 50,
  },
  emptyText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 10,
  },
  emptySubtext: {
    color: '#ccc',
    fontSize: 14,
    textAlign: 'center',
    paddingHorizontal: 20,
  },
});
