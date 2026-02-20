import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface CartItem {
  product_id: string;
  name: string;
  price: number;
  quantity: number;
  image_url: string;
  discount_price?: number;
}

interface CartStore {
  items: CartItem[];
  addItem: (item: Omit<CartItem, 'quantity'>) => void;
  removeItem: (product_id: string) => void;
  updateQuantity: (product_id: string, quantity: number) => void;
  clearCart: () => void;
  loadCart: () => Promise<void>;
  getTotal: () => number;
}

export const useCartStore = create<CartStore>((set, get) => ({
  items: [],

  addItem: (item) => {
    const { items } = get();
    const existingItem = items.find(i => i.product_id === item.product_id);
    
    let newItems;
    if (existingItem) {
      newItems = items.map(i =>
        i.product_id === item.product_id
          ? { ...i, quantity: i.quantity + 1 }
          : i
      );
    } else {
      newItems = [...items, { ...item, quantity: 1 }];
    }
    
    set({ items: newItems });
    AsyncStorage.setItem('cart', JSON.stringify(newItems));
  },

  removeItem: (product_id) => {
    const { items } = get();
    const newItems = items.filter(i => i.product_id !== product_id);
    set({ items: newItems });
    AsyncStorage.setItem('cart', JSON.stringify(newItems));
  },

  updateQuantity: (product_id, quantity) => {
    if (quantity <= 0) {
      get().removeItem(product_id);
      return;
    }
    
    const { items } = get();
    const newItems = items.map(i =>
      i.product_id === product_id ? { ...i, quantity } : i
    );
    set({ items: newItems });
    AsyncStorage.setItem('cart', JSON.stringify(newItems));
  },

  clearCart: () => {
    set({ items: [] });
    AsyncStorage.removeItem('cart');
  },

  loadCart: async () => {
    try {
      const saved = await AsyncStorage.getItem('cart');
      if (saved) {
        set({ items: JSON.parse(saved) });
      }
    } catch (error) {
      console.error('Error loading cart:', error);
    }
  },

  getTotal: () => {
    const { items } = get();
    return items.reduce((total, item) => {
      const price = item.discount_price || item.price;
      return total + (price * item.quantity);
    }, 0);
  }
}));
