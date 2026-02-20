import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  TextInput,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { api } from '../../utils/api';
import { useAuth } from '../../contexts/AuthContext';
import { useCartStore } from '../../store/cartStore';

interface Product {
  product_id: string;
  name: string;
  description: string;
  category: string;
  price: number;
  discount_price?: number;
  image_url: string;
  rating: number;
  total_reviews: number;
}

export default function HomeScreen() {
  const router = useRouter();
  const { user } = useAuth();
  const addItem = useCartStore(state => state.addItem);

  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const response = await api.get('/products');
      setProducts(response.data);
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    fetchProducts();
  };

  const filteredProducts = products.filter(p =>
    p.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const categories = [
    { name: 'Flowers', icon: 'flower', color: '#FF69B4' },
    { name: 'Cakes', icon: 'cake', color: '#FFB6C1' },
    { name: 'Chocolates', icon: 'gift', color: '#8B4513' },
  ];

  const renderProduct = (product: Product) => {
    const finalPrice = product.discount_price || product.price;
    const hasDiscount = product.discount_price && product.discount_price < product.price;

    return (
      <TouchableOpacity
        key={product.product_id}
        style={styles.productCard}
        onPress={() => router.push(`/product/${product.product_id}`)}
      >
        <Image source={{ uri: product.image_url }} style={styles.productImage} resizeMode="cover" />
        {hasDiscount && (
          <View style={styles.discountBadge}>
            <Text style={styles.discountText}>
              {Math.round(((product.price - product.discount_price!) / product.price) * 100)}% OFF
            </Text>
          </View>
        )}
        <View style={styles.productInfo}>
          <Text style={styles.productName} numberOfLines={2}>{product.name}</Text>
          <View style={styles.ratingContainer}>
            <Ionicons name="star" size={14} color="#FFD700" />
            <Text style={styles.ratingText}>{product.rating}</Text>
            <Text style={styles.reviewsText}>({product.total_reviews})</Text>
          </View>
          <View style={styles.priceContainer}>
            <Text style={styles.price}>₹{finalPrice}</Text>
            {hasDiscount && <Text style={styles.originalPrice}>₹{product.price}</Text>}
          </View>
        </View>
      </TouchableOpacity>
    );
  };

  if (loading && !refreshing) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#FF69B4" />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        <View style={styles.header}>
          <View>
            <Text style={styles.greeting}>Hello, {user?.name?.split(' ')[0] || 'Guest'}!</Text>
            <Text style={styles.subGreeting}>What would you like to send today?</Text>
          </View>
          <TouchableOpacity onPress={() => router.push('/profile')}>
            {user?.picture ? (
              <Image source={{ uri: user.picture }} style={styles.avatar} />
            ) : (
              <View style={[styles.avatar, styles.avatarPlaceholder]}>
                <Ionicons name="person" size={24} color="#fff" />
              </View>
            )}
          </TouchableOpacity>
        </View>

        <View style={styles.searchContainer}>
          <Ionicons name="search" size={20} color="#999" style={styles.searchIcon} />
          <TextInput
            style={styles.searchInput}
            placeholder="Search flowers, cakes, chocolates..."
            value={searchQuery}
            onChangeText={setSearchQuery}
          />
        </View>

        <View style={styles.categoriesContainer}>
          {categories.map((cat) => (
            <TouchableOpacity
              key={cat.name}
              style={[styles.categoryCard, { backgroundColor: cat.color + '20' }]}
              onPress={() => router.push({ pathname: '/categories', params: { category: cat.name.toLowerCase() } })}
            >
              <Ionicons name={cat.icon as any} size={32} color={cat.color} />
              <Text style={styles.categoryName}>{cat.name}</Text>
            </TouchableOpacity>
          ))}
        </View>

        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Featured Products</Text>
            <TouchableOpacity onPress={() => router.push('/categories')}>
              <Text style={styles.seeAll}>See All</Text>
            </TouchableOpacity>
          </View>
          <View style={styles.productsGrid}>
            {filteredProducts.slice(0, 6).map(renderProduct)}
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  scrollContent: {
    paddingBottom: 20,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#fff',
  },
  greeting: {
    fontSize: 24,
    fontWeight: '700',
    color: '#333',
  },
  subGreeting: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  avatar: {
    width: 48,
    height: 48,
    borderRadius: 24,
  },
  avatarPlaceholder: {
    backgroundColor: '#FF69B4',
    justifyContent: 'center',
    alignItems: 'center',
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    margin: 16,
    paddingHorizontal: 16,
    borderRadius: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  searchIcon: {
    marginRight: 8,
  },
  searchInput: {
    flex: 1,
    paddingVertical: 14,
    fontSize: 16,
    color: '#333',
  },
  categoriesContainer: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    gap: 12,
    marginBottom: 24,
  },
  categoryCard: {
    flex: 1,
    padding: 16,
    borderRadius: 16,
    alignItems: 'center',
    gap: 8,
  },
  categoryName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  section: {
    paddingHorizontal: 16,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#333',
  },
  seeAll: {
    fontSize: 14,
    color: '#FF69B4',
    fontWeight: '600',
  },
  productsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  productCard: {
    width: '48%',
    backgroundColor: '#fff',
    borderRadius: 12,
    overflow: 'hidden',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  productImage: {
    width: '100%',
    height: 150,
  },
  discountBadge: {
    position: 'absolute',
    top: 8,
    right: 8,
    backgroundColor: '#FF4444',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  discountText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: '700',
  },
  productInfo: {
    padding: 12,
  },
  productName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  ratingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    marginBottom: 8,
  },
  ratingText: {
    fontSize: 12,
    color: '#333',
    fontWeight: '600',
  },
  reviewsText: {
    fontSize: 12,
    color: '#999',
  },
  priceContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  price: {
    fontSize: 16,
    fontWeight: '700',
    color: '#FF69B4',
  },
  originalPrice: {
    fontSize: 12,
    color: '#999',
    textDecorationLine: 'line-through',
  },
});
