import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Product data
PRODUCTS = [
    # FLOWERS
    {
        "product_id": "prod_001",
        "name": "Red Roses Bouquet",
        "description": "Beautiful bouquet of fresh red roses, perfect for expressing love and affection. Contains 12 premium red roses.",
        "category": "flowers",
        "subcategory": "roses",
        "price": 899.00,
        "discount_price": 749.00,
        "image_url": "https://images.pexels.com/photos/54320/rose-roses-flowers-red-54320.jpeg",
        "stock": 50,
        "rating": 4.5,
        "total_reviews": 120,
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    },
    {
        "product_id": "prod_002",
        "name": "Tulips Arrangement",
        "description": "Vibrant tulips arrangement in assorted colors. Brings spring vibes to any room.",
        "category": "flowers",
        "subcategory": "tulips",
        "price": 1299.00,
        "discount_price": 1099.00,
        "image_url": "https://images.pexels.com/photos/103573/pexels-photo-103573.jpeg",
        "stock": 30,
        "rating": 4.7,
        "total_reviews": 85,
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    },
    {
        "product_id": "prod_003",
        "name": "Elegant Orchids",
        "description": "Premium orchids arrangement, symbolizing beauty and luxury. Long-lasting and elegant.",
        "category": "flowers",
        "subcategory": "orchids",
        "price": 1799.00,
        "discount_price": 1599.00,
        "image_url": "https://images.pexels.com/photos/2291811/pexels-photo-2291811.jpeg",
        "stock": 20,
        "rating": 4.8,
        "total_reviews": 65,
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    },
    {
        "product_id": "prod_004",
        "name": "Mixed Flower Bouquet",
        "description": "Colorful mix of seasonal flowers. Perfect for any celebration or occasion.",
        "category": "flowers",
        "subcategory": "mixed",
        "price": 1099.00,
        "discount_price": 899.00,
        "image_url": "https://images.unsplash.com/photo-1572454591674-2739f30d8c40?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjAzMjV8MHwxfHNlYXJjaHwxfHxmbG93ZXIlMjBib3VxdWV0fGVufDB8fHx8MTc3MTYxMjkzNXww&ixlib=rb-4.1.0&q=85",
        "stock": 40,
        "rating": 4.6,
        "total_reviews": 95,
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    },
    {
        "product_id": "prod_005",
        "name": "White Roses Bouquet",
        "description": "Pure white roses representing peace and innocence. Ideal for weddings and condolences.",
        "category": "flowers",
        "subcategory": "roses",
        "price": 999.00,
        "discount_price": 799.00,
        "image_url": "https://images.pexels.com/photos/14917605/pexels-photo-14917605.jpeg",
        "stock": 35,
        "rating": 4.7,
        "total_reviews": 78,
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    },
    {
        "product_id": "prod_006",
        "name": "Sunflowers Bouquet",
        "description": "Bright and cheerful sunflowers that bring sunshine to any day. Fresh and vibrant.",
        "category": "flowers",
        "subcategory": "sunflowers",
        "price": 799.00,
        "discount_price": 649.00,
        "image_url": "https://images.pexels.com/photos/1169084/pexels-photo-1169084.jpeg",
        "stock": 45,
        "rating": 4.5,
        "total_reviews": 102,
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    },
    # CAKES
    {
        "product_id": "prod_007",
        "name": "Chocolate Birthday Cake",
        "description": "Rich chocolate cake perfect for birthday celebrations. Moist and delicious with chocolate frosting.",
        "category": "cakes",
        "subcategory": "birthday",
        "price": 899.00,
        "discount_price": 749.00,
        "image_url": "https://images.pexels.com/photos/10510747/pexels-photo-10510747.jpeg",
        "stock": 25,
        "rating": 4.8,
        "total_reviews": 156,
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    },
    {
        "product_id": "prod_008",
        "name": "Vanilla Anniversary Cake",
        "description": "Classic vanilla cake perfect for anniversaries. Elegant decoration with fresh cream.",
        "category": "cakes",
        "subcategory": "anniversary",
        "price": 1099.00,
        "discount_price": 949.00,
        "image_url": "https://images.pexels.com/photos/29192489/pexels-photo-29192489.jpeg",
        "stock": 20,
        "rating": 4.7,
        "total_reviews": 89,
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    },
    {
        "product_id": "prod_009",
        "name": "Red Velvet Cake",
        "description": "Luxurious red velvet cake with cream cheese frosting. Smooth and velvety texture.",
        "category": "cakes",
        "subcategory": "specialty",
        "price": 1299.00,
        "discount_price": 1099.00,
        "image_url": "https://images.pexels.com/photos/19534496/pexels-photo-19534496.jpeg",
        "stock": 15,
        "rating": 4.9,
        "total_reviews": 134,
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    },
    {
        "product_id": "prod_010",
        "name": "Black Forest Cake",
        "description": "Classic Black Forest cake with cherries and chocolate shavings. Rich and indulgent.",
        "category": "cakes",
        "subcategory": "specialty",
        "price": 1199.00,
        "discount_price": 999.00,
        "image_url": "https://images.pexels.com/photos/19036040/pexels-photo-19036040.jpeg",
        "stock": 18,
        "rating": 4.8,
        "total_reviews": 167,
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    },
    {
        "product_id": "prod_011",
        "name": "Strawberry Delight Cake",
        "description": "Fresh strawberry cake with whipped cream and strawberry topping. Light and refreshing.",
        "category": "cakes",
        "subcategory": "fruit",
        "price": 1099.00,
        "discount_price": 899.00,
        "image_url": "https://images.pexels.com/photos/35583852/pexels-photo-35583852.jpeg",
        "stock": 22,
        "rating": 4.6,
        "total_reviews": 98,
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    },
    {
        "product_id": "prod_012",
        "name": "Celebration Cake",
        "description": "Special celebration cake with colorful decoration. Perfect for any party or event.",
        "category": "cakes",
        "subcategory": "celebration",
        "price": 1499.00,
        "discount_price": 1299.00,
        "image_url": "https://images.pexels.com/photos/1051089/pexels-photo-1051089.jpeg",
        "stock": 12,
        "rating": 4.9,
        "total_reviews": 145,
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    },
    # CHOCOLATES
    {
        "product_id": "prod_013",
        "name": "Premium Chocolate Gift Box",
        "description": "Assorted premium chocolates in an elegant gift box. Perfect for gifting.",
        "category": "chocolates",
        "subcategory": "gift_box",
        "price": 799.00,
        "discount_price": 649.00,
        "image_url": "https://images.pexels.com/photos/14275552/pexels-photo-14275552.jpeg",
        "stock": 40,
        "rating": 4.7,
        "total_reviews": 213,
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    },
    {
        "product_id": "prod_014",
        "name": "Assorted Chocolates",
        "description": "Delicious mix of milk, dark, and white chocolates. Something for everyone.",
        "category": "chocolates",
        "subcategory": "assorted",
        "price": 599.00,
        "discount_price": 499.00,
        "image_url": "https://images.pexels.com/photos/29098395/pexels-photo-29098395.jpeg",
        "stock": 55,
        "rating": 4.5,
        "total_reviews": 178,
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    },
    {
        "product_id": "prod_015",
        "name": "Dark Chocolate Truffles",
        "description": "Rich dark chocolate truffles with smooth ganache center. For chocolate lovers.",
        "category": "chocolates",
        "subcategory": "truffles",
        "price": 899.00,
        "discount_price": 749.00,
        "image_url": "https://images.pexels.com/photos/31249035/pexels-photo-31249035.png",
        "stock": 30,
        "rating": 4.8,
        "total_reviews": 156,
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    },
    {
        "product_id": "prod_016",
        "name": "Chocolate Hamper",
        "description": "Complete chocolate hamper with various treats. Ideal for special occasions.",
        "category": "chocolates",
        "subcategory": "hamper",
        "price": 1499.00,
        "discount_price": 1299.00,
        "image_url": "https://images.pexels.com/photos/16762643/pexels-photo-16762643.jpeg",
        "stock": 20,
        "rating": 4.9,
        "total_reviews": 187,
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    },
    {
        "product_id": "prod_017",
        "name": "Ferrero Rocher Box",
        "description": "Premium Ferrero Rocher chocolates. Classic and elegant gift option.",
        "category": "chocolates",
        "subcategory": "branded",
        "price": 699.00,
        "discount_price": 599.00,
        "image_url": "https://images.pexels.com/photos/754191/pexels-photo-754191.jpeg",
        "stock": 45,
        "rating": 4.8,
        "total_reviews": 234,
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    },
    {
        "product_id": "prod_018",
        "name": "Luxury Chocolate Collection",
        "description": "Hand-crafted luxury chocolates collection. Premium ingredients and exquisite flavors.",
        "category": "chocolates",
        "subcategory": "luxury",
        "price": 1999.00,
        "discount_price": 1799.00,
        "image_url": "https://images.pexels.com/photos/7538069/pexels-photo-7538069.jpeg",
        "stock": 15,
        "rating": 5.0,
        "total_reviews": 92,
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    }
]

async def seed_products():
    """Seed products into database"""
    print("Seeding products...")
    
    # Clear existing products
    await db.products.delete_many({})
    
    # Insert products
    await db.products.insert_many(PRODUCTS)
    
    print(f"Successfully seeded {len(PRODUCTS)} products!")
    
    # Create an admin user for testing
    admin_exists = await db.users.find_one({"email": "admin@delivery.com"})
    if not admin_exists:
        admin_user = {
            "user_id": "user_admin_001",
            "email": "admin@delivery.com",
            "name": "Admin User",
            "picture": None,
            "phone": "+919876543210",
            "role": "admin",
            "created_at": datetime.now(timezone.utc)
        }
        await db.users.insert_one(admin_user)
        print("Admin user created!")
        print("Email: admin@delivery.com")
        print("You need to login via Google OAuth to get session token")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_products())
