#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Delivery App
Tests all backend endpoints including public and protected routes
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys
import os

# Backend URL from environment
BACKEND_URL = "https://petal-delivery-2.preview.emergentagent.com/api"

class DeliveryAppTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session_token = None
        self.test_user_id = None
        self.test_address_id = None
        self.test_product_ids = []
        
    def log(self, message, level="INFO"):
        """Log test messages"""
        print(f"[{level}] {message}")
        
    def test_public_endpoints(self):
        """Test all public endpoints that don't require authentication"""
        self.log("=== TESTING PUBLIC ENDPOINTS ===")
        
        # Test 1: Get all products
        self.log("Testing GET /api/products")
        try:
            response = requests.get(f"{self.base_url}/products")
            if response.status_code == 200:
                products = response.json()
                self.log(f"✅ Products endpoint working - Found {len(products)} products")
                if len(products) >= 18:
                    self.log(f"✅ Expected 18+ products found: {len(products)}")
                else:
                    self.log(f"⚠️ Expected 18+ products, found only {len(products)}", "WARN")
                
                # Store some product IDs for later tests
                if products:
                    self.test_product_ids = [p['product_id'] for p in products[:3]]
                    self.log(f"Stored test product IDs: {self.test_product_ids}")
                return True
            else:
                self.log(f"❌ Products endpoint failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Products endpoint error: {str(e)}", "ERROR")
            return False
            
        # Test 2: Get single product
        if self.test_product_ids:
            self.log("Testing GET /api/products/{product_id}")
            try:
                product_id = self.test_product_ids[0]
                response = requests.get(f"{self.base_url}/products/{product_id}")
                if response.status_code == 200:
                    product = response.json()
                    self.log(f"✅ Single product endpoint working - Got product: {product['name']}")
                    return True
                else:
                    self.log(f"❌ Single product endpoint failed: {response.status_code} - {response.text}", "ERROR")
                    return False
            except Exception as e:
                self.log(f"❌ Single product endpoint error: {str(e)}", "ERROR")
                return False
        
        # Test 3: Filter by category
        self.log("Testing GET /api/products?category=flowers")
        try:
            response = requests.get(f"{self.base_url}/products?category=flowers")
            if response.status_code == 200:
                flowers = response.json()
                self.log(f"✅ Category filter working - Found {len(flowers)} flowers")
                return True
            else:
                self.log(f"❌ Category filter failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Category filter error: {str(e)}", "ERROR")
            return False
            
        # Test 4: Search products
        self.log("Testing GET /api/products?search=chocolate")
        try:
            response = requests.get(f"{self.base_url}/products?search=chocolate")
            if response.status_code == 200:
                chocolates = response.json()
                self.log(f"✅ Product search working - Found {len(chocolates)} chocolate products")
                return True
            else:
                self.log(f"❌ Product search failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Product search error: {str(e)}", "ERROR")
            return False
    
    def create_test_session(self):
        """Create a test session by directly inserting into MongoDB"""
        self.log("=== CREATING TEST SESSION ===")
        
        try:
            # We'll create a test session directly in MongoDB since OAuth requires manual intervention
            from pymongo import MongoClient
            
            # Connect to MongoDB
            client = MongoClient("mongodb://localhost:27017")
            db = client["test_database"]
            
            # Create test user
            self.test_user_id = f"user_{uuid.uuid4().hex[:12]}"
            test_user = {
                "user_id": self.test_user_id,
                "email": "test@example.com",
                "name": "Test User",
                "picture": None,
                "phone": "+91-9876543210",
                "role": "customer",
                "created_at": datetime.now(timezone.utc)
            }
            
            # Insert or update user
            db.users.replace_one(
                {"email": "test@example.com"}, 
                test_user, 
                upsert=True
            )
            
            # Create test session
            self.session_token = f"test_session_{uuid.uuid4().hex}"
            test_session = {
                "user_id": self.test_user_id,
                "session_token": self.session_token,
                "expires_at": datetime.now(timezone.utc).replace(year=2025),  # Far future
                "created_at": datetime.now(timezone.utc)
            }
            
            # Insert session
            db.user_sessions.replace_one(
                {"session_token": self.session_token},
                test_session,
                upsert=True
            )
            
            self.log(f"✅ Test session created - User ID: {self.test_user_id}")
            self.log(f"✅ Session token: {self.session_token}")
            
            client.close()
            return True
            
        except Exception as e:
            self.log(f"❌ Failed to create test session: {str(e)}", "ERROR")
            return False
    
    def test_auth_endpoints(self):
        """Test authentication endpoints"""
        self.log("=== TESTING AUTH ENDPOINTS ===")
        
        if not self.session_token:
            self.log("❌ No session token available for auth tests", "ERROR")
            return False
            
        headers = {"Authorization": f"Bearer {self.session_token}"}
        
        # Test /auth/me
        self.log("Testing GET /api/auth/me")
        try:
            response = requests.get(f"{self.base_url}/auth/me", headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                self.log(f"✅ Auth me endpoint working - User: {user_data['name']}")
                return True
            else:
                self.log(f"❌ Auth me endpoint failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Auth me endpoint error: {str(e)}", "ERROR")
            return False
    
    def test_address_endpoints(self):
        """Test address CRUD operations"""
        self.log("=== TESTING ADDRESS ENDPOINTS ===")
        
        if not self.session_token:
            self.log("❌ No session token available for address tests", "ERROR")
            return False
            
        headers = {"Authorization": f"Bearer {self.session_token}"}
        
        # Test create address
        self.log("Testing POST /api/addresses")
        address_data = {
            "label": "Home",
            "full_address": "123 Test Street, Test Area",
            "city": "Mumbai",
            "state": "Maharashtra",
            "pincode": "400001",
            "phone": "+91-9876543210",
            "is_default": True
        }
        
        try:
            response = requests.post(f"{self.base_url}/addresses", json=address_data, headers=headers)
            if response.status_code == 200:
                address = response.json()
                self.test_address_id = address['address_id']
                self.log(f"✅ Create address working - Address ID: {self.test_address_id}")
            else:
                self.log(f"❌ Create address failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Create address error: {str(e)}", "ERROR")
            return False
        
        # Test get addresses
        self.log("Testing GET /api/addresses")
        try:
            response = requests.get(f"{self.base_url}/addresses", headers=headers)
            if response.status_code == 200:
                addresses = response.json()
                self.log(f"✅ Get addresses working - Found {len(addresses)} addresses")
                return True
            else:
                self.log(f"❌ Get addresses failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Get addresses error: {str(e)}", "ERROR")
            return False
    
    def test_wishlist_endpoints(self):
        """Test wishlist operations"""
        self.log("=== TESTING WISHLIST ENDPOINTS ===")
        
        if not self.session_token or not self.test_product_ids:
            self.log("❌ No session token or product IDs available for wishlist tests", "ERROR")
            return False
            
        headers = {"Authorization": f"Bearer {self.session_token}"}
        product_id = self.test_product_ids[0]
        
        # Test add to wishlist
        self.log(f"Testing POST /api/wishlist/{product_id}")
        try:
            response = requests.post(f"{self.base_url}/wishlist/{product_id}", headers=headers)
            if response.status_code == 200:
                result = response.json()
                self.log(f"✅ Add to wishlist working - {result['message']}")
            else:
                self.log(f"❌ Add to wishlist failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Add to wishlist error: {str(e)}", "ERROR")
            return False
        
        # Test get wishlist
        self.log("Testing GET /api/wishlist")
        try:
            response = requests.get(f"{self.base_url}/wishlist", headers=headers)
            if response.status_code == 200:
                wishlist = response.json()
                self.log(f"✅ Get wishlist working - Found {len(wishlist)} items")
                return True
            else:
                self.log(f"❌ Get wishlist failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Get wishlist error: {str(e)}", "ERROR")
            return False
    
    def test_order_endpoints(self):
        """Test order creation and retrieval"""
        self.log("=== TESTING ORDER ENDPOINTS ===")
        
        if not self.session_token or not self.test_address_id or not self.test_product_ids:
            self.log("❌ Missing requirements for order tests", "ERROR")
            return False
            
        headers = {"Authorization": f"Bearer {self.session_token}"}
        
        # Test create order
        self.log("Testing POST /api/orders")
        order_data = {
            "items": [
                {
                    "product_id": self.test_product_ids[0],
                    "quantity": 2,
                    "price": 299.0
                }
            ],
            "address_id": self.test_address_id,
            "delivery_slot": {
                "date": "2024-12-25",
                "time_slot": "morning"
            },
            "payment_method": "cod"
        }
        
        try:
            response = requests.post(f"{self.base_url}/orders", json=order_data, headers=headers)
            if response.status_code == 200:
                order = response.json()
                self.log(f"✅ Create order working - Order ID: {order['order_id']}")
                test_order_id = order['order_id']
            else:
                self.log(f"❌ Create order failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Create order error: {str(e)}", "ERROR")
            return False
        
        # Test get orders
        self.log("Testing GET /api/orders")
        try:
            response = requests.get(f"{self.base_url}/orders", headers=headers)
            if response.status_code == 200:
                orders = response.json()
                self.log(f"✅ Get orders working - Found {len(orders)} orders")
                return True
            else:
                self.log(f"❌ Get orders failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Get orders error: {str(e)}", "ERROR")
            return False
    
    def test_review_endpoints(self):
        """Test review creation and retrieval"""
        self.log("=== TESTING REVIEW ENDPOINTS ===")
        
        if not self.session_token or not self.test_product_ids:
            self.log("❌ Missing requirements for review tests", "ERROR")
            return False
            
        headers = {"Authorization": f"Bearer {self.session_token}"}
        product_id = self.test_product_ids[0]
        
        # Test create review
        self.log("Testing POST /api/reviews")
        review_data = {
            "product_id": product_id,
            "rating": 5,
            "comment": "Excellent product! Very fresh and beautiful."
        }
        
        try:
            response = requests.post(f"{self.base_url}/reviews", json=review_data, headers=headers)
            if response.status_code == 200:
                review = response.json()
                self.log(f"✅ Create review working - Review ID: {review['review_id']}")
            else:
                self.log(f"❌ Create review failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Create review error: {str(e)}", "ERROR")
            return False
        
        # Test get reviews
        self.log(f"Testing GET /api/reviews/{product_id}")
        try:
            response = requests.get(f"{self.base_url}/reviews/{product_id}")
            if response.status_code == 200:
                reviews = response.json()
                self.log(f"✅ Get reviews working - Found {len(reviews)} reviews")
                return True
            else:
                self.log(f"❌ Get reviews failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Get reviews error: {str(e)}", "ERROR")
            return False
    
    def create_admin_session(self):
        """Create an admin session for admin endpoint testing"""
        self.log("=== CREATING ADMIN SESSION ===")
        
        try:
            from pymongo import MongoClient
            
            client = MongoClient("mongodb://localhost:27017")
            db = client["test_database"]
            
            # Create admin user
            admin_user_id = f"admin_{uuid.uuid4().hex[:12]}"
            admin_user = {
                "user_id": admin_user_id,
                "email": "admin@example.com",
                "name": "Admin User",
                "picture": None,
                "phone": "+91-9876543210",
                "role": "admin",  # Admin role
                "created_at": datetime.now(timezone.utc)
            }
            
            db.users.replace_one(
                {"email": "admin@example.com"}, 
                admin_user, 
                upsert=True
            )
            
            # Create admin session
            admin_session_token = f"admin_session_{uuid.uuid4().hex}"
            admin_session = {
                "user_id": admin_user_id,
                "session_token": admin_session_token,
                "expires_at": datetime.now(timezone.utc).replace(year=2025),
                "created_at": datetime.now(timezone.utc)
            }
            
            db.user_sessions.replace_one(
                {"session_token": admin_session_token},
                admin_session,
                upsert=True
            )
            
            self.log(f"✅ Admin session created - User ID: {admin_user_id}")
            
            client.close()
            return admin_session_token
            
        except Exception as e:
            self.log(f"❌ Failed to create admin session: {str(e)}", "ERROR")
            return None
    
    def test_admin_endpoints(self):
        """Test admin-only endpoints"""
        self.log("=== TESTING ADMIN ENDPOINTS ===")
        
        admin_token = self.create_admin_session()
        if not admin_token:
            self.log("❌ Could not create admin session", "ERROR")
            return False
            
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Test get all orders (admin)
        self.log("Testing GET /api/admin/orders")
        try:
            response = requests.get(f"{self.base_url}/admin/orders", headers=headers)
            if response.status_code == 200:
                orders = response.json()
                self.log(f"✅ Admin get orders working - Found {len(orders)} orders")
            else:
                self.log(f"❌ Admin get orders failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Admin get orders error: {str(e)}", "ERROR")
            return False
        
        # Test analytics
        self.log("Testing GET /api/admin/analytics")
        try:
            response = requests.get(f"{self.base_url}/admin/analytics", headers=headers)
            if response.status_code == 200:
                analytics = response.json()
                self.log(f"✅ Admin analytics working - Total orders: {analytics['total_orders']}")
                self.log(f"   Total revenue: ₹{analytics['total_revenue']}")
                self.log(f"   Total products: {analytics['total_products']}")
                self.log(f"   Total users: {analytics['total_users']}")
                return True
            else:
                self.log(f"❌ Admin analytics failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Admin analytics error: {str(e)}", "ERROR")
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        self.log("🚀 STARTING COMPREHENSIVE BACKEND API TESTING")
        self.log(f"Backend URL: {self.base_url}")
        
        results = {
            "public_endpoints": False,
            "test_session_creation": False,
            "auth_endpoints": False,
            "address_endpoints": False,
            "wishlist_endpoints": False,
            "order_endpoints": False,
            "review_endpoints": False,
            "admin_endpoints": False
        }
        
        # Test public endpoints first
        results["public_endpoints"] = self.test_public_endpoints()
        
        # Create test session for protected endpoints
        results["test_session_creation"] = self.create_test_session()
        
        if results["test_session_creation"]:
            results["auth_endpoints"] = self.test_auth_endpoints()
            results["address_endpoints"] = self.test_address_endpoints()
            results["wishlist_endpoints"] = self.test_wishlist_endpoints()
            results["order_endpoints"] = self.test_order_endpoints()
            results["review_endpoints"] = self.test_review_endpoints()
        
        # Test admin endpoints
        results["admin_endpoints"] = self.test_admin_endpoints()
        
        # Summary
        self.log("\n" + "="*60)
        self.log("🏁 BACKEND TESTING SUMMARY")
        self.log("="*60)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{test_name.replace('_', ' ').title()}: {status}")
            if result:
                passed += 1
        
        self.log(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            self.log("🎉 ALL BACKEND TESTS PASSED!")
            return True
        else:
            self.log(f"⚠️ {total - passed} tests failed")
            return False

if __name__ == "__main__":
    tester = DeliveryAppTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)