import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  FlatList,
  ActivityIndicator,
  Alert,
  RefreshControl,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { highlightsAPI } from '../services/api';

export default function HighlightsScreen({ navigation, route }) {
  const { leagueId } = route.params;
  const [highlights, setHighlights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [currentWeek, setCurrentWeek] = useState(1);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    loadHighlights();
  }, [leagueId, currentWeek]);

  const loadHighlights = async () => {
    setLoading(true);
    try {
      const response = await highlightsAPI.getHighlightsForWeek(leagueId, currentWeek);
      setHighlights(response.data);
    } catch (error) {
      console.error('Error loading highlights:', error);
      Alert.alert('Error', 'Failed to load highlights');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadHighlights();
    setRefreshing(false);
  };

  const handleGenerateHighlights = async () => {
    setGenerating(true);
    try {
      await highlightsAPI.generateHighlights({
        league_id: leagueId,
        week: currentWeek,
        season: 2024,
      });
      
      Alert.alert(
        'Highlights Generating',
        'Your highlights are being processed. This may take a few minutes.',
        [{ text: 'OK', onPress: () => loadHighlights() }]
      );
    } catch (error) {
      Alert.alert('Error', 'Failed to generate highlights');
    } finally {
      setGenerating(false);
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

  const renderWeekSelector = () => (
    <View style={styles.weekSelector}>
      <TouchableOpacity
        style={styles.weekButton}
        onPress={() => setCurrentWeek(Math.max(1, currentWeek - 1))}
      >
        <Text style={styles.weekButtonText}>‹</Text>
      </TouchableOpacity>
      
      <Text style={styles.weekText}>Week {currentWeek}</Text>
      
      <TouchableOpacity
        style={styles.weekButton}
        onPress={() => setCurrentWeek(currentWeek + 1)}
      >
        <Text style={styles.weekButtonText}>›</Text>
      </TouchableOpacity>
    </View>
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
        {renderWeekSelector()}
        
        <View style={styles.actions}>
          <TouchableOpacity
            style={[styles.generateButton, generating && styles.buttonDisabled]}
            onPress={handleGenerateHighlights}
            disabled={generating}
          >
            <Text style={styles.generateButtonText}>
              {generating ? 'Generating...' : 'Generate Highlights'}
            </Text>
          </TouchableOpacity>
        </View>

        <FlatList
          data={highlights}
          renderItem={renderHighlightItem}
          keyExtractor={(item) => item.id.toString()}
          style={styles.highlightsList}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={handleRefresh}
              tintColor="#007AFF"
            />
          }
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Text style={styles.emptyText}>No highlights found for Week {currentWeek}</Text>
              <Text style={styles.emptySubtext}>
                Tap "Generate Highlights" to create your personalized highlight reel
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
  weekSelector: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 20,
  },
  weekButton: {
    backgroundColor: '#333',
    borderRadius: 20,
    width: 40,
    height: 40,
    alignItems: 'center',
    justifyContent: 'center',
  },
  weekButtonText: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold',
  },
  weekText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    marginHorizontal: 20,
  },
  actions: {
    marginBottom: 20,
  },
  generateButton: {
    backgroundColor: '#007AFF',
    borderRadius: 10,
    padding: 15,
    alignItems: 'center',
  },
  buttonDisabled: {
    backgroundColor: '#555',
  },
  generateButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
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
