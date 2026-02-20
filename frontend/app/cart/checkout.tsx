import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { api } from '../../utils/api';
import { useCartStore } from '../../store/cartStore';

interface Address {
  address_id: string;
  label: string;
  full_address: string;
  city: string;
  state: string;
  pincode: string;
  phone: string;
  is_default: boolean;
}

export default function CheckoutScreen() {
  const router = useRouter();
  const { items, getTotal, clearCart } = useCartStore();
  const [addresses, setAddresses] = useState<Address[]>([]);
  const [selectedAddressId, setSelectedAddressId] = useState<string | null>(null);
  const [deliveryDate, setDeliveryDate] = useState('');
  const [deliverySlot, setDeliverySlot] = useState('morning');
  const [paymentMethod, setPaymentMethod] = useState('cod');
  const [loading, setLoading] = useState(false);
  const [showAddAddress, setShowAddAddress] = useState(false);

  // New address form
  const [newAddress, setNewAddress] = useState({
    label: 'Home',
    full_address: '',
    city: '',
    state: '',
    pincode: '',
    phone: '',
  });

  useEffect(() => {
    fetchAddresses();
  }, []);

  const fetchAddresses = async () => {
    try {
      const response = await api.get('/addresses');
      setAddresses(response.data);
      const defaultAddr = response.data.find((a: Address) => a.is_default);
      if (defaultAddr) {
        setSelectedAddressId(defaultAddr.address_id);
      } else if (response.data.length > 0) {
        setSelectedAddressId(response.data[0].address_id);
      }
    } catch (error) {
      console.error('Error fetching addresses:', error);
    }
  };

  const handleAddAddress = async () => {
    if (!newAddress.full_address || !newAddress.city || !newAddress.phone) {
      Alert.alert('Error', 'Please fill all required fields');
      return;
    }

    try {
      await api.post('/addresses', newAddress);
      setShowAddAddress(false);
      setNewAddress({
        label: 'Home',
        full_address: '',
        city: '',
        state: '',
        pincode: '',
        phone: '',
      });
      fetchAddresses();
      Alert.alert('Success', 'Address added successfully');
    } catch (error) {
      console.error('Error adding address:', error);
      Alert.alert('Error', 'Failed to add address');
    }
  };

  const handlePlaceOrder = async () => {
    if (!selectedAddressId) {
      Alert.alert('Error', 'Please select a delivery address');
      return;
    }

    if (!deliveryDate) {
      Alert.alert('Error', 'Please select a delivery date');
      return;
    }

    try {
      setLoading(true);
      const orderData = {
        items: items.map(item => ({
          product_id: item.product_id,
          quantity: item.quantity,
          price: item.discount_price || item.price,
        })),
        address_id: selectedAddressId,
        delivery_slot: {
          date: deliveryDate,
          time_slot: deliverySlot,
        },
        payment_method: paymentMethod,
      };

      const response = await api.post('/orders', orderData);
      clearCart();
      Alert.alert(
        'Order Placed!',
        `Your order #${response.data.order_id} has been placed successfully.`,
        [
          {
            text: 'View Order',
            onPress: () => router.replace(`/order/${response.data.order_id}`),
          },
        ]
      );
    } catch (error: any) {
      console.error('Error placing order:', error);
      Alert.alert('Error', error.response?.data?.detail || 'Failed to place order');
    } finally {
      setLoading(false);
    }
  };

  const total = getTotal();

  if (items.length === 0) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.emptyContainer}>
          <Text>Your cart is empty</Text>
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => router.back()}
          >
            <Text style={styles.backButtonText}>Go Back</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={24} color="#333" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Checkout</Text>
        <View style={{ width: 24 }} />
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Delivery Address */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Delivery Address</Text>
          {addresses.map((address) => (
            <TouchableOpacity
              key={address.address_id}
              style={[
                styles.addressCard,
                selectedAddressId === address.address_id && styles.addressCardSelected,
              ]}
              onPress={() => setSelectedAddressId(address.address_id)}
            >
              <View style={styles.addressHeader}>
                <Text style={styles.addressLabel}>{address.label}</Text>
                {selectedAddressId === address.address_id && (
                  <Ionicons name="checkmark-circle" size={24} color="#FF69B4" />
                )}
              </View>
              <Text style={styles.addressText}>{address.full_address}</Text>
              <Text style={styles.addressText}>
                {address.city}, {address.state} - {address.pincode}
              </Text>
              <Text style={styles.addressPhone}>Phone: {address.phone}</Text>
            </TouchableOpacity>
          ))}

          {showAddAddress ? (
            <View style={styles.addAddressForm}>
              <TextInput
                style={styles.input}
                placeholder="Address Label (Home/Work)"
                value={newAddress.label}
                onChangeText={(text) => setNewAddress({ ...newAddress, label: text })}
              />
              <TextInput
                style={styles.input}
                placeholder="Full Address *"
                value={newAddress.full_address}
                onChangeText={(text) => setNewAddress({ ...newAddress, full_address: text })}
                multiline
              />
              <TextInput
                style={styles.input}
                placeholder="City *"
                value={newAddress.city}
                onChangeText={(text) => setNewAddress({ ...newAddress, city: text })}
              />
              <TextInput
                style={styles.input}
                placeholder="State"
                value={newAddress.state}
                onChangeText={(text) => setNewAddress({ ...newAddress, state: text })}
              />
              <TextInput
                style={styles.input}
                placeholder="Pincode"
                value={newAddress.pincode}
                onChangeText={(text) => setNewAddress({ ...newAddress, pincode: text })}
                keyboardType="number-pad"
              />
              <TextInput
                style={styles.input}
                placeholder="Phone Number *"
                value={newAddress.phone}
                onChangeText={(text) => setNewAddress({ ...newAddress, phone: text })}
                keyboardType="phone-pad"
              />
              <View style={styles.addAddressButtons}>
                <TouchableOpacity
                  style={[styles.button, styles.cancelButton]}
                  onPress={() => setShowAddAddress(false)}
                >
                  <Text style={styles.cancelButtonText}>Cancel</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.button, styles.saveButton]}
                  onPress={handleAddAddress}
                >
                  <Text style={styles.saveButtonText}>Save Address</Text>
                </TouchableOpacity>
              </View>
            </View>
          ) : (
            <TouchableOpacity
              style={styles.addAddressButton}
              onPress={() => setShowAddAddress(true)}
            >
              <Ionicons name="add-circle-outline" size={20} color="#FF69B4" />
              <Text style={styles.addAddressText}>Add New Address</Text>
            </TouchableOpacity>
          )}
        </View>

        {/* Delivery Slot */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Delivery Slot</Text>
          <TextInput
            style={styles.input}
            placeholder="Delivery Date (YYYY-MM-DD)"
            value={deliveryDate}
            onChangeText={setDeliveryDate}
          />
          <View style={styles.slotContainer}>
            {['morning', 'afternoon', 'evening'].map((slot) => (
              <TouchableOpacity
                key={slot}
                style={[
                  styles.slotChip,
                  deliverySlot === slot && styles.slotChipSelected,
                ]}
                onPress={() => setDeliverySlot(slot)}
              >
                <Text
                  style={[
                    styles.slotText,
                    deliverySlot === slot && styles.slotTextSelected,
                  ]}
                >
                  {slot.charAt(0).toUpperCase() + slot.slice(1)}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Payment Method */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Payment Method</Text>
          {[
            { id: 'cod', name: 'Cash on Delivery', icon: 'cash' },
            { id: 'phonepe', name: 'PhonePe (Coming Soon)', icon: 'phone-portrait', disabled: true },
            { id: 'paytm', name: 'Paytm (Coming Soon)', icon: 'wallet', disabled: true },
          ].map((method) => (
            <TouchableOpacity
              key={method.id}
              style={[
                styles.paymentCard,
                paymentMethod === method.id && styles.paymentCardSelected,
                method.disabled && styles.paymentCardDisabled,
              ]}
              onPress={() => !method.disabled && setPaymentMethod(method.id)}
              disabled={method.disabled}
            >
              <View style={styles.paymentLeft}>
                <Ionicons name={method.icon as any} size={24} color="#666" />
                <Text style={[styles.paymentName, method.disabled && styles.disabledText]}>
                  {method.name}
                </Text>
              </View>
              {paymentMethod === method.id && !method.disabled && (
                <Ionicons name="checkmark-circle" size={24} color="#FF69B4" />
              )}
            </TouchableOpacity>
          ))}
        </View>

        {/* Order Summary */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Order Summary</Text>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Items ({items.length}):</Text>
            <Text style={styles.summaryValue}>₹{total.toFixed(2)}</Text>
          </View>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Delivery:</Text>
            <Text style={styles.deliveryFree}>FREE</Text>
          </View>
          <View style={styles.divider} />
          <View style={styles.summaryRow}>
            <Text style={styles.totalLabel}>Total Amount:</Text>
            <Text style={styles.totalValue}>₹{total.toFixed(2)}</Text>
          </View>
        </View>
      </ScrollView>

      <View style={styles.footer}>
        <TouchableOpacity
          style={styles.placeOrderButton}
          onPress={handlePlaceOrder}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <>
              <Text style={styles.placeOrderText}>Place Order</Text>
              <Text style={styles.placeOrderAmount}>₹{total.toFixed(2)}</Text>
            </>
          )}
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#333',
  },
  scrollContent: {
    padding: 16,
    paddingBottom: 100,
  },
  section: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#333',
    marginBottom: 16,
  },
  addressCard: {
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
  },
  addressCardSelected: {
    borderColor: '#FF69B4',
    borderWidth: 2,
  },
  addressHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  addressLabel: {
    fontSize: 16,
    fontWeight: '700',
    color: '#333',
  },
  addressText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  addressPhone: {
    fontSize: 14,
    color: '#666',
    fontWeight: '600',
  },
  addAddressButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    paddingVertical: 12,
    borderWidth: 1,
    borderColor: '#FF69B4',
    borderRadius: 8,
    borderStyle: 'dashed',
  },
  addAddressText: {
    color: '#FF69B4',
    fontSize: 14,
    fontWeight: '600',
  },
  addAddressForm: {
    marginTop: 12,
  },
  input: {
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
    marginBottom: 12,
  },
  addAddressButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  button: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  cancelButton: {
    backgroundColor: '#f0f0f0',
  },
  cancelButtonText: {
    color: '#666',
    fontWeight: '600',
  },
  saveButton: {
    backgroundColor: '#FF69B4',
  },
  saveButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
  slotContainer: {
    flexDirection: 'row',
    gap: 12,
  },
  slotChip: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    backgroundColor: '#f0f0f0',
    alignItems: 'center',
  },
  slotChipSelected: {
    backgroundColor: '#FF69B4',
  },
  slotText: {
    fontSize: 14,
    color: '#666',
    fontWeight: '600',
  },
  slotTextSelected: {
    color: '#fff',
  },
  paymentCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
  },
  paymentCardSelected: {
    borderColor: '#FF69B4',
    borderWidth: 2,
  },
  paymentCardDisabled: {
    opacity: 0.5,
  },
  paymentLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  paymentName: {
    fontSize: 14,
    color: '#333',
    fontWeight: '600',
  },
  disabledText: {
    color: '#999',
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  summaryLabel: {
    fontSize: 14,
    color: '#666',
  },
  summaryValue: {
    fontSize: 14,
    color: '#333',
    fontWeight: '600',
  },
  deliveryFree: {
    fontSize: 14,
    color: '#4CAF50',
    fontWeight: '600',
  },
  divider: {
    height: 1,
    backgroundColor: '#f0f0f0',
    marginVertical: 12,
  },
  totalLabel: {
    fontSize: 16,
    fontWeight: '700',
    color: '#333',
  },
  totalValue: {
    fontSize: 16,
    fontWeight: '700',
    color: '#FF69B4',
  },
  footer: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: '#fff',
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
  },
  placeOrderButton: {
    backgroundColor: '#FF69B4',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 12,
  },
  placeOrderText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '700',
  },
  placeOrderAmount: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '700',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  backButton: {
    marginTop: 16,
    paddingVertical: 12,
    paddingHorizontal: 24,
    backgroundColor: '#FF69B4',
    borderRadius: 8,
  },
  backButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
});
