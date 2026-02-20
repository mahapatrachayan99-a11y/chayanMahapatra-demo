import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as WebBrowser from 'expo-web-browser';
import * as Linking from 'expo-linking';
import { Platform } from 'react-native';
import { api } from '../utils/api';

interface User {
  user_id: string;
  email: string;
  name: string;
  picture?: string;
  phone?: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: () => Promise<void>;
  logout: () => Promise<void>;
  token: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL || 'https://petal-delivery-2.preview.emergentagent.com';

  useEffect(() => {
    loadSession();
  }, []);

  const loadSession = async () => {
    try {
      const savedToken = await AsyncStorage.getItem('session_token');
      if (savedToken) {
        setToken(savedToken);
        await fetchUser(savedToken);
      }
    } catch (error) {
      console.error('Error loading session:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchUser = async (sessionToken: string) => {
    try {
      const response = await api.get('/auth/me', {
        headers: { Authorization: `Bearer ${sessionToken}` }
      });
      setUser(response.data);
    } catch (error) {
      console.error('Error fetching user:', error);
      await logout();
    }
  };

  const login = async () => {
    try {
      const redirectUrl = Platform.OS === 'web'
        ? `${BACKEND_URL}/`
        : Linking.createURL('/');

      const authUrl = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;

      if (Platform.OS === 'web') {
        // For web, redirect directly
        window.location.href = authUrl;
      } else {
        // For mobile, use WebBrowser
        const result = await WebBrowser.openAuthSessionAsync(authUrl, redirectUrl);
        
        if (result.type === 'success') {
          const url = result.url;
          const sessionId = extractSessionId(url);
          
          if (sessionId) {
            await exchangeSessionId(sessionId);
          }
        }
      }
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const extractSessionId = (url: string): string | null => {
    // Extract from hash (#session_id=...)
    const hashMatch = url.match(/#session_id=([^&]+)/);
    if (hashMatch) return hashMatch[1];
    
    // Extract from query (?session_id=...)
    const queryMatch = url.match(/[?&]session_id=([^&]+)/);
    if (queryMatch) return queryMatch[1];
    
    return null;
  };

  const exchangeSessionId = async (sessionId: string) => {
    try {
      const response = await api.post('/auth/session', { session_id: sessionId });
      const { session_token } = response.data;
      
      await AsyncStorage.setItem('session_token', session_token);
      setToken(session_token);
      await fetchUser(session_token);
    } catch (error) {
      console.error('Error exchanging session:', error);
      throw error;
    }
  };

  const logout = async () => {
    try {
      if (token) {
        await api.post('/auth/logout', {}, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      await AsyncStorage.removeItem('session_token');
      setUser(null);
      setToken(null);
    }
  };

  // Handle deep link for web
  useEffect(() => {
    if (Platform.OS === 'web') {
      const handleWebAuth = async () => {
        const hash = window.location.hash;
        const sessionId = extractSessionId(hash);
        
        if (sessionId) {
          window.history.replaceState({}, document.title, '/');
          await exchangeSessionId(sessionId);
        }
      };
      
      handleWebAuth();
    }
  }, []);

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout, token }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
