import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../contexts/AuthContext';

export default function LoginScreen() {
  const { login, isLoading } = useAuth();

  const handleLogin = async () => {
    try {
      await login();
    } catch (error) {
      console.error('Login failed:', error);
      alert('Login failed. Please try again.');
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.header}>
          <View style={styles.iconContainer}>
            <Ionicons name="gift" size={80} color="#FF69B4" />
          </View>
          <Text style={styles.title}>Welcome to{' \n'}Petal Delivery</Text>
          <Text style={styles.subtitle}>
            Send love with flowers, cakes & chocolates
          </Text>
        </View>

        <View style={styles.features}>
          <View style={styles.feature}>
            <Ionicons name="flower" size={32} color="#FF69B4" />
            <Text style={styles.featureText}>Fresh Flowers</Text>
          </View>
          <View style={styles.feature}>
            <Ionicons name="cake" size={32} color="#FF69B4" />
            <Text style={styles.featureText}>Delicious Cakes</Text>
          </View>
          <View style={styles.feature}>
            <Ionicons name="gift" size={32} color="#FF69B4" />
            <Text style={styles.featureText}>Premium Chocolates</Text>
          </View>
        </View>

        <TouchableOpacity
          style={styles.button}
          onPress={handleLogin}
          disabled={isLoading}
        >
          <Ionicons name="logo-google" size={24} color="#fff" style={styles.buttonIcon} />
          <Text style={styles.buttonText}>
            {isLoading ? 'Signing in...' : 'Sign in with Google'}
          </Text>
        </TouchableOpacity>

        <Text style={styles.terms}>
          By continuing, you agree to our Terms of Service and Privacy Policy
        </Text>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  content: {
    flex: 1,
    padding: 24,
    justifyContent: 'space-between',
  },
  header: {
    alignItems: 'center',
    marginTop: 60,
  },
  iconContainer: {
    marginBottom: 24,
  },
  title: {
    fontSize: 32,
    fontWeight: '700',
    color: '#333',
    textAlign: 'center',
    marginBottom: 16,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
  features: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginVertical: 48,
  },
  feature: {
    alignItems: 'center',
    gap: 8,
  },
  featureText: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
  },
  button: {
    backgroundColor: '#FF69B4',
    paddingVertical: 16,
    borderRadius: 12,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  buttonIcon: {
    marginRight: 12,
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
  terms: {
    fontSize: 12,
    color: '#999',
    textAlign: 'center',
    marginTop: 24,
  },
});
