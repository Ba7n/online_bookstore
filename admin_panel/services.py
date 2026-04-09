"""
admin_panel/services.py
══════════════════════
Service layer for Firestore operations.
All database queries are isolated here for clean architecture.
"""

import uuid
from decimal import Decimal
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple
from firebase_config.firebase import db, Collections
from .utils import (
    convert_decimal_to_float,
    calculate_subtotal,
    normalize_payment_status,
    denormalize_payment_status,
    get_transaction_id,
)

class UserService:
    """Service for user management operations."""
    
    @staticmethod
    def get_all_users(limit: int = 100, offset: int = 0) -> Tuple[List[Dict], int]:
        """Fetch all users with pagination."""
        try:
            # Get total count
            docs = db.collection(Collections.USERS).get()
            total = len(docs)
            
            # Get paginated results
            users = []
            for doc in docs[offset:offset + limit]:
                user_data = doc.to_dict()
                user_data['user_id'] = doc.id
                users.append(user_data)
            
            return users, total
        except Exception as e:
            raise Exception(f"Error fetching users: {str(e)}")
    
    @staticmethod
    def search_users(query: str, limit: int = 100) -> List[Dict]:
        """Search users by name or email."""
        try:
            users = []
            docs = db.collection(Collections.USERS).get()
            
            query_lower = query.lower()
            for doc in docs[:limit]:
                user_data = doc.to_dict()
                username = user_data.get('username', '').lower()
                email = user_data.get('email', '').lower()
                
                if query_lower in username or query_lower in email:
                    user_data['user_id'] = doc.id
                    users.append(user_data)
            
            return users[:limit]
        except Exception as e:
            raise Exception(f"Error searching users: {str(e)}")
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[Dict]:
        """Fetch a single user by ID."""
        try:
            doc = db.collection(Collections.USERS).document(user_id).get()
            if not doc.exists:
                return None
            
            user_data = doc.to_dict()
            user_data['user_id'] = user_id
            return user_data
        except Exception as e:
            raise Exception(f"Error fetching user: {str(e)}")
    
    @staticmethod
    def delete_user(user_id: str) -> bool:
        """Delete a user and related data."""
        try:
            # Delete user
            db.collection(Collections.USERS).document(user_id).delete()
            
            # Delete addresses
            addresses = db.collection(Collections.ADDRESSES).where('user_id', '==', user_id).get()
            for addr in addresses:
                addr.reference.delete()
            
            # Delete cart
            carts = db.collection(Collections.CARTS).where('user_id', '==', user_id).get()
            for cart in carts:
                cart.reference.delete()
            
            # Delete wishlist
            wishlists = db.collection(Collections.WISHLISTS).where('user_id', '==', user_id).get()
            for wishlist in wishlists:
                wishlist.reference.delete()
            
            return True
        except Exception as e:
            raise Exception(f"Error deleting user: {str(e)}")
    
    @staticmethod
    def get_user_stats() -> Dict:
        """Get user statistics."""
        try:
            docs = db.collection(Collections.USERS).get()
            total_users = len(docs)
            admin_users = sum(1 for doc in docs if doc.to_dict().get('is_admin', False))
            
            return {
                'total_users': total_users,
                'admin_users': admin_users,
                'regular_users': total_users - admin_users
            }
        except Exception as e:
            raise Exception(f"Error fetching user stats: {str(e)}")


class ProductService:
    """Service for product management operations."""
    
    @staticmethod
    def get_all_products(limit: int = 100, offset: int = 0) -> Tuple[List[Dict], int]:
        """Fetch all products with pagination."""
        try:
            docs = db.collection(Collections.PRODUCTS).get()
            total = len(docs)
            
            products = []
            for doc in docs[offset:offset + limit]:
                product_data = doc.to_dict()
                product_data['product_id'] = doc.id
                products.append(product_data)
            
            return sorted(products, key=lambda x: x.get('created_at', ''), reverse=True), total
        except Exception as e:
            raise Exception(f"Error fetching products: {str(e)}")
    
    @staticmethod
    def search_products(query: str, limit: int = 100) -> List[Dict]:
        """Search products by name or author."""
        try:
            products = []
            docs = db.collection(Collections.PRODUCTS).get()
            
            query_lower = query.lower()
            for doc in docs[:limit]:
                product_data = doc.to_dict()
                name = product_data.get('name', '').lower()
                author = product_data.get('author', '').lower()
                
                if query_lower in name or query_lower in author:
                    product_data['product_id'] = doc.id
                    products.append(product_data)
            
            return products[:limit]
        except Exception as e:
            raise Exception(f"Error searching products: {str(e)}")
    
    @staticmethod
    def get_product_by_id(product_id: str) -> Optional[Dict]:
        """Fetch a single product by ID."""
        try:
            doc = db.collection(Collections.PRODUCTS).document(product_id).get()
            if not doc.exists:
                return None
            
            product_data = doc.to_dict()
            product_data['product_id'] = product_id
            return product_data
        except Exception as e:
            raise Exception(f"Error fetching product: {str(e)}")
    
    @staticmethod
    def create_product(data: Dict) -> str:
        """Create a new product.
        
        Converts all Decimal values to float before saving to Firestore.
        Firestore cannot serialize Python Decimal objects.
        """
        try:
            product_id = str(uuid.uuid4())
            data['product_id'] = product_id
            data['created_at'] = datetime.now(timezone.utc).isoformat()
            data['stock'] = int(data.get('stock', 0))
            
            # Convert price to float (NOT Decimal - Firestore can't serialize Decimal)
            if 'price' in data:
                data['price'] = float(Decimal(str(data.get('price', '0'))))
            
            # Safety: Convert all Decimal values in data structure
            data = convert_decimal_to_float(data)
            
            db.collection(Collections.PRODUCTS).document(product_id).set(data)
            return product_id
        except Exception as e:
            raise Exception(f"Error creating product: {str(e)}")
    
    @staticmethod
    def update_product(product_id: str, data: Dict) -> bool:
        """Update an existing product.
        
        Converts all Decimal values to float before saving to Firestore.
        Firestore cannot serialize Python Decimal objects.
        """
        try:
            if 'product_id' in data:
                del data['product_id']
            if 'created_at' in data:
                del data['created_at']
            
            data['updated_at'] = datetime.now(timezone.utc).isoformat()
            data['stock'] = int(data.get('stock', 0))
            
            # Convert price to float (NOT Decimal - Firestore can't serialize Decimal)
            if 'price' in data:
                data['price'] = float(Decimal(str(data.get('price', '0'))))
            
            # Safety: Convert all Decimal values in data structure
            data = convert_decimal_to_float(data)
            
            db.collection(Collections.PRODUCTS).document(product_id).update(data)
            return True
        except Exception as e:
            raise Exception(f"Error updating product: {str(e)}")
    
    @staticmethod
    def delete_product(product_id: str) -> bool:
        """Delete a product."""
        try:
            db.collection(Collections.PRODUCTS).document(product_id).delete()
            return True
        except Exception as e:
            raise Exception(f"Error deleting product: {str(e)}")
    
    @staticmethod
    def get_categories() -> List[Dict]:
        """Fetch all categories."""
        try:
            categories = []
            docs = db.collection(Collections.CATEGORIES).get()
            for doc in docs:
                cat_data = doc.to_dict()
                cat_data['category_id'] = doc.id
                categories.append(cat_data)
            
            return sorted(categories, key=lambda x: x.get('category_name', ''))
        except Exception as e:
            raise Exception(f"Error fetching categories: {str(e)}")
    
    @staticmethod
    def get_product_stats() -> Dict:
        """Get product statistics."""
        try:
            docs = db.collection(Collections.PRODUCTS).get()
            total_products = len(docs)
            total_stock = sum(int(doc.to_dict().get('stock', 0)) for doc in docs)
            low_stock = sum(1 for doc in docs if int(doc.to_dict().get('stock', 0)) < 5)
            
            return {
                'total_products': total_products,
                'total_stock': total_stock,
                'low_stock_items': low_stock
            }
        except Exception as e:
            raise Exception(f"Error fetching product stats: {str(e)}")


class OrderService:
    """Service for order management operations."""
    
    @staticmethod
    def get_all_orders(limit: int = 100, offset: int = 0) -> Tuple[List[Dict], int]:
        """Fetch all orders with pagination."""
        try:
            docs = db.collection(Collections.ORDERS).get()
            total = len(docs)
            
            orders = []
            for doc in docs[offset:offset + limit]:
                order_data = doc.to_dict()
                order_data['order_id'] = doc.id
                orders.append(order_data)
            
            return sorted(orders, key=lambda x: x.get('created_at', ''), reverse=True), total
        except Exception as e:
            raise Exception(f"Error fetching orders: {str(e)}")
    
    @staticmethod
    def filter_orders_by_status(status: str, limit: int = 100) -> List[Dict]:
        """Filter orders by status."""
        try:
            docs = db.collection(Collections.ORDERS).where('order_status', '==', status).get()
            
            orders = []
            for doc in docs[:limit]:
                order_data = doc.to_dict()
                order_data['order_id'] = doc.id
                orders.append(order_data)
            
            return orders
        except Exception as e:
            raise Exception(f"Error filtering orders: {str(e)}")
    
    @staticmethod
    def get_order_by_id(order_id: str) -> Optional[Dict]:
        """Fetch a single order by ID.
        
        Ensures subtotal is calculated for all order items.
        Subtotal = quantity * price (always as float).
        """
        try:
            doc = db.collection(Collections.ORDERS).document(order_id).get()
            if not doc.exists:
                return None
            
            order_data = doc.to_dict()
            order_data['order_id'] = order_id
            
            # Fetch order items and ensure subtotal is calculated
            order_items = []
            items_docs = db.collection(Collections.ORDER_ITEMS).where('order_id', '==', order_id).get()
            for item_doc in items_docs:
                item_data = item_doc.to_dict()
                item_data['item_id'] = item_doc.id
                
                # Ensure subtotal is calculated and present
                if 'subtotal' not in item_data or item_data['subtotal'] is None:
                    # Calculate subtotal as quantity * price
                    quantity = float(item_data.get('quantity', 0))
                    price = float(item_data.get('price', 0))
                    item_data['subtotal'] = calculate_subtotal(quantity, price)
                
                # Ensure price and subtotal are floats (not Decimal)
                item_data['price'] = float(item_data.get('price', 0))
                item_data['subtotal'] = float(item_data.get('subtotal', 0))
                
                order_items.append(item_data)
            
            order_data['items'] = order_items
            return order_data
        except Exception as e:
            raise Exception(f"Error fetching order: {str(e)}")
    
    @staticmethod
    def update_order_status(order_id: str, new_status: str) -> bool:
        """Update order status."""
        try:
            valid_statuses = ['Pending', 'Shipped', 'Out for Delivery', 'Delivered', 'Cancelled']
            if new_status not in valid_statuses:
                raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
            
            db.collection(Collections.ORDERS).document(order_id).update({
                'order_status': new_status,
                'updated_at': datetime.now(timezone.utc).isoformat()
            })
            return True
        except Exception as e:
            raise Exception(f"Error updating order status: {str(e)}")
    
    @staticmethod
    def get_order_stats() -> Dict:
        """Get order statistics."""
        try:
            docs = db.collection(Collections.ORDERS).get()
            total_orders = len(docs)
            
            status_count = {
                'Pending': 0,
                'Shipped': 0,
                'Out for Delivery': 0,
                'Delivered': 0,
                'Cancelled': 0
            }
            
            total_revenue = Decimal('0')
            for doc in docs:
                order_data = doc.to_dict()
                status = order_data.get('order_status', 'Pending')
                if status in status_count:
                    status_count[status] += 1
                
                total_revenue += Decimal(str(order_data.get('total_amount', 0)))
            
            return {
                'total_orders': total_orders,
                'total_revenue': float(total_revenue),
                'status_count': status_count
            }
        except Exception as e:
            raise Exception(f"Error fetching order stats: {str(e)}")
    
    @staticmethod
    def get_recent_orders(limit: int = 5) -> List[Dict]:
        """Get recent orders."""
        try:
            docs = db.collection(Collections.ORDERS).get()
            orders = []
            for doc in docs[:limit]:
                order_data = doc.to_dict()
                order_data['order_id'] = doc.id
                orders.append(order_data)
            
            return sorted(orders, key=lambda x: x.get('created_at', ''), reverse=True)[:limit]
        except Exception as e:
            raise Exception(f"Error fetching recent orders: {str(e)}")


class PaymentService:
    """Service for payment management operations."""
    
    @staticmethod
    def get_all_payments(limit: int = 100, offset: int = 0) -> Tuple[List[Dict], int]:
        """Fetch all payments with pagination."""
        try:
            docs = db.collection(Collections.PAYMENTS).get()
            total = len(docs)
            
            payments = []
            for doc in docs[offset:offset + limit]:
                payment_data = doc.to_dict()
                payment_data['payment_id'] = doc.id
                
                # Normalize payment status for UI (Paid → success, Failed → failed)
                payment_status = payment_data.get('payment_status', 'Pending')
                payment_data['payment_status'] = normalize_payment_status(payment_status)
                
                # Extract transaction ID safely
                payment_data['transaction_id'] = get_transaction_id(payment_data)
                
                payments.append(payment_data)
            
            return sorted(payments, key=lambda x: x.get('payment_date', ''), reverse=True), total
        except Exception as e:
            raise Exception(f"Error fetching payments: {str(e)}")
    
    @staticmethod
    def filter_payments_by_status(status: str, limit: int = 100) -> List[Dict]:
        """Filter payments by status (success/failed).
        
        Args:
            status: UI status ('success', 'failed', etc.)
            limit: Maximum number of results
        
        Returns:
            List of normalized payment dictionaries
        """
        try:
            # Convert UI status to database status
            db_status = denormalize_payment_status(status)
            if not db_status:
                return []
            
            docs = db.collection(Collections.PAYMENTS).where('payment_status', '==', db_status).get()
            
            payments = []
            for doc in docs[:limit]:
                payment_data = doc.to_dict()
                payment_data['payment_id'] = doc.id
                
                # Normalize payment status for UI
                payment_status = payment_data.get('payment_status', 'Pending')
                payment_data['payment_status'] = normalize_payment_status(payment_status)
                
                # Extract transaction ID safely
                payment_data['transaction_id'] = get_transaction_id(payment_data)
                
                payments.append(payment_data)
            
            return sorted(payments, key=lambda x: x.get('payment_date', ''), reverse=True)[:limit]
        except Exception as e:
            raise Exception(f"Error filtering payments: {str(e)}")
    
    @staticmethod
    def get_payment_stats() -> Dict:
        """Get payment statistics."""
        try:
            docs = db.collection(Collections.PAYMENTS).get()
            total_payments = len(docs)
            
            successful = 0
            failed = 0
            total_amount = Decimal('0')
            
            for doc in docs:
                payment_data = doc.to_dict()
                db_status = payment_data.get('payment_status', 'Pending')
                normalized_status = normalize_payment_status(db_status)
                
                if normalized_status == 'success':
                    successful += 1
                    total_amount += Decimal(str(payment_data.get('amount', 0)))
                else:
                    failed += 1
            
            return {
                'total_payments': total_payments,
                'successful_payments': successful,
                'failed_payments': failed,
                'total_amount': float(total_amount)
            }
        except Exception as e:
            raise Exception(f"Error fetching payment stats: {str(e)}")


class CartService:
    """Service for cart management operations."""
    
    @staticmethod
    def get_all_carts(limit: int = 100, offset: int = 0) -> Tuple[List[Dict], int]:
        """Fetch all carts with pagination."""
        try:
            docs = db.collection(Collections.CARTS).get()
            total = len(docs)
            
            carts = []
            for doc in docs[offset:offset + limit]:
                cart_data = doc.to_dict()
                cart_data['cart_id'] = doc.id
                
                # Fetch cart items
                items_docs = db.collection(Collections.CART_ITEMS).where('cart_id', '==', doc.id).get()
                items = []
                for item_doc in items_docs:
                    item_data = item_doc.to_dict()
                    item_data['cart_item_id'] = item_doc.id
                    items.append(item_data)
                
                cart_data['items'] = items
                carts.append(cart_data)
            
            return carts, total
        except Exception as e:
            raise Exception(f"Error fetching carts: {str(e)}")


class WishlistService:
    """Service for wishlist management operations."""
    
    @staticmethod
    def get_all_wishlists(limit: int = 100, offset: int = 0) -> Tuple[List[Dict], int]:
        """Fetch all wishlists with pagination."""
        try:
            docs = db.collection(Collections.WISHLISTS).get()
            total = len(docs)
            
            wishlists = []
            for doc in docs[offset:offset + limit]:
                wishlist_data = doc.to_dict()
                wishlist_data['wishlist_id'] = doc.id
                
                # Fetch wishlist items
                items_docs = db.collection(Collections.WISHLIST_ITEMS).where('wishlist_id', '==', doc.id).get()
                items = []
                for item_doc in items_docs:
                    item_data = item_doc.to_dict()
                    item_data['wishlist_item_id'] = item_doc.id
                    items.append(item_data)
                
                wishlist_data['items'] = items
                wishlists.append(wishlist_data)
            
            return wishlists, total
        except Exception as e:
            raise Exception(f"Error fetching wishlists: {str(e)}")
