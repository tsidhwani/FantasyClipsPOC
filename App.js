import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, View } from 'react-native';

import LoginScreen from './src/screens/LoginScreen';
import RegisterScreen from './src/screens/RegisterScreen';
import LeagueConnectScreen from './src/screens/LeagueConnectScreen';
import HighlightsScreen from './src/screens/HighlightsScreen';
import PlayerHighlightsScreen from './src/screens/PlayerHighlightsScreen';
import VideoPlayerScreen from './src/screens/VideoPlayerScreen';

const Stack = createStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <View style={styles.container}>
        <StatusBar style="auto" />
        <Stack.Navigator
          initialRouteName="Login"
          screenOptions={{
            headerStyle: {
              backgroundColor: '#1a1a1a',
            },
            headerTintColor: '#fff',
            headerTitleStyle: {
              fontWeight: 'bold',
            },
          }}
        >
          <Stack.Screen 
            name="Login" 
            component={LoginScreen} 
            options={{ title: 'Fantasy Clips' }}
          />
          <Stack.Screen 
            name="Register" 
            component={RegisterScreen} 
            options={{ title: 'Create Account' }}
          />
          <Stack.Screen 
            name="LeagueConnect" 
            component={LeagueConnectScreen} 
            options={{ title: 'Connect League' }}
          />
          <Stack.Screen 
            name="Highlights" 
            component={HighlightsScreen} 
            options={{ title: 'Your Highlights' }}
          />
          <Stack.Screen 
            name="PlayerHighlights" 
            component={PlayerHighlightsScreen} 
            options={{ title: 'Player Highlights' }}
          />
          <Stack.Screen 
            name="VideoPlayer" 
            component={VideoPlayerScreen} 
            options={{ title: 'Watch Highlight' }}
          />
        </Stack.Navigator>
      </View>
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a',
  },
});
