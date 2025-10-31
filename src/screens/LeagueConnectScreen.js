import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  FlatList,
  ActivityIndicator,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { leaguesAPI } from '../services/api';

export default function LeagueConnectScreen({ navigation }) {
  const [sleeperUsername, setSleeperUsername] = useState('');
  const [leagueId, setLeagueId] = useState('');
  const [loading, setLoading] = useState(false);
  const [leagues, setLeagues] = useState([]);
  const [loadingLeagues, setLoadingLeagues] = useState(false);

  useEffect(() => {
    loadUserLeagues();
  }, []);

  const loadUserLeagues = async () => {
    setLoadingLeagues(true);
    try {
      const response = await leaguesAPI.getUserLeagues();
      setLeagues(response.data);
    } catch (error) {
      console.error('Error loading leagues:', error);
    } finally {
      setLoadingLeagues(false);
    }
  };

  const handleConnectLeague = async () => {
    if (!sleeperUsername || !leagueId) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    setLoading(true);
    try {
      const response = await leaguesAPI.connectLeague({
        sleeper_username: sleeperUsername,
        league_id: leagueId,
      });

      Alert.alert('Success', 'League connected successfully!');
      loadUserLeagues();
      setSleeperUsername('');
      setLeagueId('');
    } catch (error) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to connect league');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectLeague = (league) => {
    navigation.navigate('Highlights', { leagueId: league.id });
  };

  const renderLeagueItem = ({ item }) => (
    <TouchableOpacity
      style={styles.leagueItem}
      onPress={() => handleSelectLeague(item)}
    >
      <Text style={styles.leagueName}>{item.name}</Text>
      <Text style={styles.leagueSeason}>Season {item.season}</Text>
    </TouchableOpacity>
  );

  return (
    <LinearGradient
      colors={['#1a1a1a', '#2d2d2d']}
      style={styles.container}
    >
      <View style={styles.content}>
        <Text style={styles.title}>Connect Your League</Text>
        <Text style={styles.subtitle}>Link your Sleeper fantasy league</Text>

        <View style={styles.form}>
          <TextInput
            style={styles.input}
            placeholder="Sleeper Username"
            placeholderTextColor="#666"
            value={sleeperUsername}
            onChangeText={setSleeperUsername}
            autoCapitalize="none"
          />

          <TextInput
            style={styles.input}
            placeholder="League ID"
            placeholderTextColor="#666"
            value={leagueId}
            onChangeText={setLeagueId}
            autoCapitalize="none"
          />

          <TouchableOpacity
            style={[styles.button, loading && styles.buttonDisabled]}
            onPress={handleConnectLeague}
            disabled={loading}
          >
            <Text style={styles.buttonText}>
              {loading ? 'Connecting...' : 'Connect League'}
            </Text>
          </TouchableOpacity>
        </View>

        <View style={styles.leaguesSection}>
          <Text style={styles.sectionTitle}>Your Leagues</Text>
          {loadingLeagues ? (
            <ActivityIndicator size="large" color="#007AFF" />
          ) : (
            <FlatList
              data={leagues}
              renderItem={renderLeagueItem}
              keyExtractor={(item) => item.id.toString()}
              style={styles.leaguesList}
              ListEmptyComponent={
                <Text style={styles.emptyText}>No leagues connected yet</Text>
              }
            />
          )}
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
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#ccc',
    textAlign: 'center',
    marginBottom: 30,
  },
  form: {
    marginBottom: 30,
  },
  input: {
    backgroundColor: '#333',
    borderRadius: 10,
    padding: 15,
    marginBottom: 15,
    color: '#fff',
    fontSize: 16,
  },
  button: {
    backgroundColor: '#007AFF',
    borderRadius: 10,
    padding: 15,
    alignItems: 'center',
  },
  buttonDisabled: {
    backgroundColor: '#555',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  leaguesSection: {
    flex: 1,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 15,
  },
  leaguesList: {
    flex: 1,
  },
  leagueItem: {
    backgroundColor: '#333',
    borderRadius: 10,
    padding: 15,
    marginBottom: 10,
  },
  leagueName: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  leagueSeason: {
    color: '#ccc',
    fontSize: 14,
  },
  emptyText: {
    color: '#666',
    textAlign: 'center',
    fontSize: 16,
    marginTop: 20,
  },
});
