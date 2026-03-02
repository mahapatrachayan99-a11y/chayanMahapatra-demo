from fastapi import FastAPI, APIRouter, HTTPException, Depends, Header, Response, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import httpx

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# ================== MODELS ==================

class User(BaseModel):
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    phone: Optional[str] = None
    role: str = "customer"  # customer or admin
    created_at: datetime

class SessionDataResponse(BaseModel):
    id: str
    email: str
    name: str
    picture: Optional[str] = None
    session_token: str

class Address(BaseModel):
    address_id: str
    user_id: str
    label: str  # Home, Work, etc.
    full_address: str
    city: str
    state: str
    pincode: str
    phone: str
    is_default: bool = False
    created_at: datetime

class AddressCreate(BaseModel):
    label: str
    full_address: str
    city: str
    state: str
    pincode: str
    phone: str
    is_default: bool = False

class Product(BaseModel):
    product_id: str
    name: str
    description: str
    category: str  # flowers, cakes, chocolates
    subcategory: str
    price: float
    discount_price: Optional[float] = None
    image_url: str
    stock: int
    rating: float = 0.0
    total_reviews: int = 0
    is_active: bool = True
    created_at: datetime

class ProductCreate(BaseModel):
    name: str
    description: str
    category: str
    subcategory: str
    price: float
    discount_price: Optional[float] = None
    image_url: str
    stock: int

class Review(BaseModel):
    review_id: str
    product_id: str
    user_id: str
    user_name: str
    rating: int
    comment: str
    created_at: datetime

class ReviewCreate(BaseModel):
    product_id: str
    rating: int
    comment: str

class WishlistItem(BaseModel):
    wishlist_id: str
    user_id: str
    product_id: str
    added_at: datetime

class CartItem(BaseModel):
    product_id: str
    quantity: int
    price: float

class OrderItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    price: float
    total: float

class DeliverySlot(BaseModel):
    date: str
    time_slot: str  # morning, afternoon, evening

class Order(BaseModel):
    order_id: str
    user_id: str
    items: List[OrderItem]
    total_amount: float
    delivery_address: dict
    delivery_slot: DeliverySlot
    payment_method: str  # cod, phonepe, paytm
    payment_status: str = "pending"  # pending, completed, failed
    order_status: str = "placed"  # placed, confirmed, out_for_delivery, delivered, cancelled
    created_at: datetime
    updated_at: datetime

class OrderCreate(BaseModel):
    items: List[CartItem]
    address_id: str
    delivery_slot: DeliverySlot
    payment_method: str

class OrderStatusUpdate(BaseModel):
    order_status: str

# ================== AUTH HELPERS ==================

async def exchange_session_id(session_id: str) -> dict:
    """Exchange session_id for user data from Emergent Auth"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
            headers={"X-Session-ID": session_id}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid session_id")
        return response.json()

async def get_current_user(authorization: Optional[str] = Header(None)) -> User:
    """Get current authenticated user"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Remove 'Bearer ' prefix if present
    session_token = authorization.replace("Bearer ", "")
    
    # Find session in database
    session = await db.user_sessions.find_one(
        {"session_token": session_token},
        {"_id": 0}
    )
    
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    # Check if session is expired
    expires_at = session["expires_at"]
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session expired")
    
    # Get user
    user_doc = await db.users.find_one(
        {"user_id": session["user_id"]},
        {"_id": 0}
    )
    
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    return User(**user_doc)

async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Verify user is admin"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# ================== AUTH ROUTES ==================

@api_router.post("/auth/session")
async def create_session(request: Request):
    """Exchange session_id for session_token"""
    body = await request.json()
    session_id = body.get("session_id")
    
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id required")
    
    # Exchange session_id for user data
    user_data = await exchange_session_id(session_id)
    
    # Check if user exists
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    existing_user = await db.users.find_one(
        {"email": user_data["email"]},
        {"_id": 0}
    )
    
    if not existing_user:
        # Create new user
        new_user = {
            "user_id": user_id,
            "email": user_data["email"],
            "name": user_data["name"],
            "picture": user_data.get("picture"),
            "phone": None,
            "role": "customer",
            "created_at": datetime.now(timezone.utc)
        }
        await db.users.insert_one(new_user)
    else:
        user_id = existing_user["user_id"]
    
    # Create session
    session_token = user_data["session_token"]
    session = {
        "user_id": user_id,
        "session_token": session_token,
        "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
        "created_at": datetime.now(timezone.utc)
    }
    await db.user_sessions.insert_one(session)
    
    return SessionDataResponse(**user_data)

@api_router.get("/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return current_user

@api_router.post("/auth/logout")
async def logout(authorization: Optional[str] = Header(None)):
    """Logout user"""
    if authorization:
        session_token = authorization.replace("Bearer ", "")
        await db.user_sessions.delete_one({"session_token": session_token})
    return {"message": "Logged out successfully"}

# ================== PRODUCT ROUTES ==================

@api_router.get("/products")
async def get_products(category: Optional[str] = None, search: Optional[str] = None):
    """Get all products with optional filtering"""
    query = {"is_active": True}
    if category:
        query["category"] = category
    if search:
        query["name"] = {"$regex": search, "$options": "i"}
    
    products = await db.products.find(query, {"_id": 0}).to_list(1000)
    return products

@api_router.get("/products/{product_id}")
async def get_product(product_id: str):
    """Get product by ID"""
    product = await db.products.find_one({"product_id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@api_router.post("/products", dependencies=[Depends(get_admin_user)])
async def create_product(product: ProductCreate, current_user: User = Depends(get_admin_user)):
    """Create new product (Admin only)"""
    product_id = f"prod_{uuid.uuid4().hex[:12]}"
    new_product = Product(
        product_id=product_id,
        **product.dict(),
        created_at=datetime.now(timezone.utc)
    )
    await db.products.insert_one(new_product.dict())
    return new_product

@api_router.put("/products/{product_id}", dependencies=[Depends(get_admin_user)])
async def update_product(product_id: str, product: ProductCreate):
    """Update product (Admin only)"""
    result = await db.products.update_one(
        {"product_id": product_id},
        {"$set": product.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product updated successfully"}

@api_router.delete("/products/{product_id}", dependencies=[Depends(get_admin_user)])
async def delete_product(product_id: str):
    """Delete product (Admin only)"""
    result = await db.products.update_one(
        {"product_id": product_id},
        {"$set": {"is_active": False}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

# ================== REVIEW ROUTES ==================

@api_router.get("/reviews/{product_id}")
async def get_reviews(product_id: str):
    """Get reviews for a product"""
    reviews = await db.reviews.find({"product_id": product_id}, {"_id": 0}).to_list(1000)
    return reviews

@api_router.post("/reviews")
async def create_review(review: ReviewCreate, current_user: User = Depends(get_current_user)):
    """Create a review"""
    review_id = f"rev_{uuid.uuid4().hex[:12]}"
    new_review = Review(
        review_id=review_id,
        user_id=current_user.user_id,
        user_name=current_user.name,
        **review.dict(),
        created_at=datetime.now(timezone.utc)
    )
    await db.reviews.insert_one(new_review.dict())
    
    # Update product rating
    reviews = await db.reviews.find({"product_id": review.product_id}, {"_id": 0}).to_list(1000)
    avg_rating = sum(r["rating"] for r in reviews) / len(reviews)
    await db.products.update_one(
        {"product_id": review.product_id},
        {"$set": {"rating": round(avg_rating, 1), "total_reviews": len(reviews)}}
    )
    
    return new_review

# ================== WISHLIST ROUTES ==================

@api_router.get("/wishlist")
async def get_wishlist(current_user: User = Depends(get_current_user)):
    """Get user's wishlist"""
    wishlist = await db.wishlist.find({" user_id": current_user.user_id}, {"_id": 0}).to_list(1000)
    
    # Batch query for products to avoid N+1
    product_ids = [item["product_id"] for item in wishlist]
    if not product_ids:
        return []
    
    products = await db.products.find(
        {"product_id": {"$in": product_ids}, "is_active": True},
        {"_id": 0}
    ).to_list(1000)
    
    return products

@api_router.post("/wishlist/{product_id}")
async def add_to_wishlist(product_id: str, current_user: User = Depends(get_current_user)):
    """Add product to wishlist"""
    # Check if already in wishlist
    existing = await db.wishlist.find_one({
        "user_id": current_user.user_id,
        "product_id": product_id
    })
    if existing:
        return {"message": "Already in wishlist"}
    
    wishlist_id = f"wish_{uuid.uuid4().hex[:12]}"
    new_item = WishlistItem(
        wishlist_id=wishlist_id,
        user_id=current_user.user_id,
        product_id=product_id,
        added_at=datetime.now(timezone.utc)
    )
    await db.wishlist.insert_one(new_item.dict())
    return {"message": "Added to wishlist"}

@api_router.delete("/wishlist/{product_id}")
async def remove_from_wishlist(product_id: str, current_user: User = Depends(get_current_user)):
    """Remove product from wishlist"""
    result = await db.wishlist.delete_one({
        "user_id": current_user.user_id,
        "product_id": product_id
    })
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found in wishlist")
    return {"message": "Removed from wishlist"}

# ================== ADDRESS ROUTES ==================

@api_router.get("/addresses")
async def get_addresses(current_user: User = Depends(get_current_user)):
    """Get user's addresses"""
    addresses = await db.addresses.find({"user_id": current_user.user_id}, {"_id": 0}).to_list(1000)
    return addresses

@api_router.post("/addresses")
async def create_address(address: AddressCreate, current_user: User = Depends(get_current_user)):
    """Create new address"""
    # If this is default, unset other defaults
    if address.is_default:
        await db.addresses.update_many(
            {"user_id": current_user.user_id},
            {"$set": {"is_default": False}}
        )
    
    address_id = f"addr_{uuid.uuid4().hex[:12]}"
    new_address = Address(
        address_id=address_id,
        user_id=current_user.user_id,
        **address.dict(),
        created_at=datetime.now(timezone.utc)
    )
    await db.addresses.insert_one(new_address.dict())
    return new_address

@api_router.delete("/addresses/{address_id}")
async def delete_address(address_id: str, current_user: User = Depends(get_current_user)):
    """Delete address"""
    result = await db.addresses.delete_one({
        "address_id": address_id,
        "user_id": current_user.user_id
    })
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Address not found")
    return {"message": "Address deleted successfully"}

# ================== ORDER ROUTES ==================

@api_router.post("/orders")
async def create_order(order: OrderCreate, current_user: User = Depends(get_current_user)):
    """Create new order"""
    # Get address
    address = await db.addresses.find_one({"address_id": order.address_id}, {"_id": 0})
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    
    # Calculate total and prepare order items
    order_items = []
    total = 0
    for item in order.items:
        product = await db.products.find_one({"product_id": item.product_id}, {"_id": 0})
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        
        item_total = item.quantity * product["price"]
        total += item_total
        
        order_items.append(OrderItem(
            product_id=item.product_id,
            product_name=product["name"],
            quantity=item.quantity,
            price=product["price"],
            total=item_total
        ))
    
    # Create order
    order_id = f"order_{uuid.uuid4().hex[:12]}"
    new_order = Order(
        order_id=order_id,
        user_id=current_user.user_id,
        items=order_items,
        total_amount=total,
        delivery_address=address,
        delivery_slot=order.delivery_slot,
        payment_method=order.payment_method,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    await db.orders.insert_one(new_order.dict())
    return new_order

@api_router.get("/orders")
async def get_orders(current_user: User = Depends(get_current_user)):
    """Get user's orders"""
    orders = await db.orders.find(
        {"user_id": current_user.user_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(1000)
    return orders

@api_router.get("/orders/{order_id}")
async def get_order(order_id: str, current_user: User = Depends(get_current_user)):
    """Get order details"""
    order = await db.orders.find_one(
        {"order_id": order_id, "user_id": current_user.user_id},
        {"_id": 0}
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

# ================== ADMIN ROUTES ==================

@api_router.get("/admin/orders")
async def get_all_orders(current_user: User = Depends(get_admin_user)):
    """Get all orders (Admin only)"""
    orders = await db.orders.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return orders

@api_router.put("/admin/orders/{order_id}/status")
async def update_order_status(
    order_id: str,
    status_update: OrderStatusUpdate,
    current_user: User = Depends(get_admin_user)
):
    """Update order status (Admin only)"""
    result = await db.orders.update_one(
        {"order_id": order_id},
        {
            "$set": {
                "order_status": status_update.order_status,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order status updated successfully"}

@api_router.get("/admin/analytics")
async def get_analytics(current_user: User = Depends(get_admin_user)):
    """Get analytics data (Admin only)"""
    # Total orders
    total_orders = await db.orders.count_documents({})
    
    # Total revenue
    orders = await db.orders.find({"payment_status": "completed"}, {"_id": 0}).to_list(10000)
    total_revenue = sum(order["total_amount"] for order in orders)
    
    # Total products
    total_products = await db.products.count_documents({"is_active": True})
    
    # Total users
    total_users = await db.users.count_documents({"role": "customer"})
    
    # Orders by status
    orders_by_status = {}
    all_orders = await db.orders.find({}, {"_id": 0}).to_list(10000)
    for order in all_orders:
        status = order["order_status"]
        orders_by_status[status] = orders_by_status.get(status, 0) + 1
    
    return {
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "total_products": total_products,
        "total_users": total_users,
        "orders_by_status": orders_by_status
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
