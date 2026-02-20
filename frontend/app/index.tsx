import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image } from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '../contexts/AuthContext';
import { Ionicons } from '@expo/vector-icons';

export default function Index() {
  const router = useRouter();
  const { user, isLoading } = useAuth();

  React.useEffect(() => {
    if (!isLoading) {
      if (user) {
        router.replace('/(tabs)');
      } else {
        router.replace('/auth/login');
      }
    }
  }, [user, isLoading]);

  return (
    <View style={styles.container}>
      <View style={styles.iconContainer}>
        <Ionicons name="gift" size={80} color="#FF69B4" />
      </View>
      <Text style={styles.title}>Petal Delivery</Text>
      <Text style={styles.subtitle}>Loading...</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  iconContainer: {
    marginBottom: 24,
  },
  title: {
    fontSize: 32,
    fontWeight: '700',
    color: '#333',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
  }
});
