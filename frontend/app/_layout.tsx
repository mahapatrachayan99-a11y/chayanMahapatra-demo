import React, { useEffect } from 'react';
import { Stack } from 'expo-router';
import { AuthProvider } from '../contexts/AuthContext';
import { useCartStore } from '../store/cartStore';

export default function RootLayout() {
  const loadCart = useCartStore(state => state.loadCart);

  useEffect(() => {
    loadCart();
  }, []);

  return (
    <AuthProvider>
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="index" />
        <Stack.Screen name="(tabs)" />
        <Stack.Screen name="auth/login" />
        <Stack.Screen name="product/[id]" />
        <Stack.Screen name="cart/checkout" />
        <Stack.Screen name="order/[id]" />
      </Stack>
    </AuthProvider>
  );
}
