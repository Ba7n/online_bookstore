# Online Bookstore E-commerce Backend API

A scalable, production-ready Django REST Framework backend for an online bookstore e-commerce platform.

## Project Overview

This backend API provides comprehensive e-commerce functionality including:
- User authentication and profile management
- Product catalog with filtering and search
- Shopping cart management
- Order processing and tracking
- Payment integration
- Wishlist functionality

## Tech Stack

- **Python 3.9+**
- **Django 4.2.0**
- **Django REST Framework 3.14.0**
- **PostgreSQL**
- **JWT Authentication**
- **Docker (optional)**

## Features

### Accounts Module
- User registration and login with JWT authentication
- Profile management
- Address management (multiple addresses per user)
- User authentication using JWT tokens

### Catalog Module
- Product listing with pagination
- Product filtering by category
- Product search functionality
- Admin product management (CRUD)
- Category management

### Cart Module
- Create shopping cart per user
- Add/remove items from cart
- Update item quantities
- Get cart total and item count
- Clear entire cart

### Orders Module
- Checkout from cart
- Create orders with order confirmation
- Order history for users
- Order detail view
- Order status tracking
- Order address management

### Payments Module
- Create payment records
- Update payment status (pending, completed, failed, refunded)
- Transaction tracking
- Payment method support (Credit Card, Debit Card, Net Banking, UPI, Wallet)

### Wishlist Module
- Add products to wishlist
- Remove products from wishlist
- View wishlist items
- Check if product is in wishlist

## Database Schema

All tables follow the exact schema specified in the requirements with proper relationships:

```
users
├── addresses
├── carts
│   └── cart_items
│       └── products
├── wishlist_items
│   └── products
└── orders
    ├── order_items
    │   └── products
    ├── order_addresses
    └── payments
```

## Installation

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- pip and virtualenv

### Setup Steps

1. **Clone the repository**
```bash
cd online_bookstore/bookstore_project
```

2. **Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Create .env file**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Collect static files**
```bash
python manage.py collectstatic --noinput
```

8. **Run development server**
```bash
python manage.py runserver
```

Server will be available at `http://localhost:8000`

## API Endpoints

### Authentication (`/api/v1/auth/`)
- `POST /auth/register/` - Register new user
- `POST /auth/login/` - Login user
- `GET /profile/` - Get user profile (protected)
- `PUT /profile/update/` - Update profile (protected)
- `GET /addresses/` - List addresses (protected)
- `POST /addresses/` - Create address (protected)
- `GET /addresses/<id>/` - Get address detail (protected)
- `PUT /addresses/<id>/` - Update address (protected)
- `DELETE /addresses/<id>/` - Delete address (protected)

### Catalog (`/api/v1/catalog/`)
- `GET /categories/` - List all categories
- `POST /categories/` - Create category (admin only)
- `GET /products/` - List products with filtering, search, pagination
- `GET /products/detail/` - Get product details
- `POST /products/` - Create product (admin only)
- `PUT /products/` - Update product (admin only)
- `DELETE /products/` - Delete product (admin only)

### Cart (`/api/v1/cart/`)
- `GET /` - Get user cart (protected)
- `POST /` - Create cart (protected)
- `POST /add-item/` - Add item to cart (protected)
- `PUT /update-item/` - Update cart item quantity (protected)
- `DELETE /remove-item/` - Remove item from cart (protected)
- `DELETE /clear/` - Clear entire cart (protected)

### Orders (`/api/v1/orders/`)
- `GET /` - List user orders (protected)
- `GET /detail/` - Get order details (protected)
- `POST /checkout/` - Create order from cart (protected)
- `PUT /update-status/` - Update order status (admin only)

### Payments (`/api/v1/payments/`)
- `GET /` - Get payment for order (protected)
- `POST /create/` - Create payment record (protected)
- `PUT /update/` - Update payment status (protected)

### Wishlist (`/api/v1/wishlist/`)
- `GET /` - List wishlist items (protected)
- `POST /add/` - Add to wishlist (protected)
- `DELETE /remove/` - Remove from wishlist (protected)
- `GET /check/` - Check if in wishlist (protected)

## Example API Requests

### User Registration
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "phone": "+919876543210",
    "password": "SecurePassword123",
    "password_confirm": "SecurePassword123"
  }'
```

### User Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "SecurePassword123"
  }'
```

### List Products
```bash
curl -X GET "http://localhost:8000/api/v1/catalog/products/?page=1&page_size=10&category_id=1" \
  -H "Content-Type: application/json"
```

### Search Products
```bash
curl -X GET "http://localhost:8000/api/v1/catalog/products/?search=python" \
  -H "Content-Type: application/json"
```

### Add to Cart
```bash
curl -X POST http://localhost:8000/api/v1/cart/add-item/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "product": 1,
    "quantity": 2
  }'
```

### Checkout
```bash
curl -X POST http://localhost:8000/api/v1/orders/checkout/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "address_id": 1
  }'
```

## Authentication

The API uses JWT (JSON Web Token) authentication. To authenticate:

1. **Register or login** to get a JWT token
2. **Include token** in all protected requests:
```bash
Authorization: Bearer <your_jwt_token>
```

## Pagination

List endpoints support pagination:
- `?page=1` - Page number (default: 1)
- `?page_size=10` - Items per page (default: 10, max: 100)

## Filtering & Search

Product endpoints support:
- Filter by category: `?category_id=1`
- Search: `?search=book_name_or_author`
- Ordering: `?ordering=-created_at` or `?ordering=price`

## Error Handling

All API responses follow a consistent format:
```json
{
  "error": "Error message",
  "details": {}
}
```

## Admin Panel

Access Django admin at: `http://localhost:8000/admin/`

Manage:
- Users and addresses
- Products and categories
- Cart items
- Orders and order items
- Payments
- Wishlist items

## Project Structure

```
bookstore_project/
├── manage.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── apps.py
│
├── catalog/
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── apps.py
│
├── cart/
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── apps.py
│
├── orders/
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── apps.py
│
├── payments/
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── apps.py
│
├── wishlist/
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── apps.py
│
├── utils/
│   ├── auth.py           # JWT authentication utilities
│   ├── permissions.py    # Custom permissions
│   ├── helpers.py        # Helper functions
│   └── __init__.py
│
└── services/
    ├── cart_service.py       # Cart business logic
    ├── order_service.py      # Order business logic
    ├── payment_service.py    # Payment business logic
    ├── product_service.py    # Wishlist business logic
    └── __init__.py
```

## Best Practices Implemented

✅ **Clean Architecture**
- Modular app structure
- Separation of concerns (models, serializers, views, services)
- Reusable service layer for business logic

✅ **API Design**
- RESTful API endpoints
- Consistent response format
- Proper HTTP status codes
- Pagination and filtering

✅ **Security**
- JWT authentication
- Custom permissions
- Input validation via serializers
- CORS configuration

✅ **Database**
- Proper relationships and foreign keys
- Indexed queries for performance
- Atomic transactions for consistency
- Optimized queries

✅ **Code Quality**
- Clear model definitions
- Descriptive docstrings
- Type hints in services
- Error handling

## Environment Variables

Create `.env` file with:
```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration - PostgreSQL
DB_ENGINE=django.db.backends.postgresql
DB_NAME=online_bookstore
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
JWT_REFRESH_EXPIRATION_DAYS=7

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Email Configuration (optional)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## Running Tests

```bash
python manage.py test
```

## Production Deployment

1. Set `DEBUG=False` in .env
2. Use PostgreSQL database
3. Set strong `SECRET_KEY`
4. Configure allowed hosts
5. Use environment-specific settings
6. Set up logging
7. Configure CORS appropriately
8. Use a production server (Gunicorn, uWSGI)
9. Set up SSL/TLS
10. Configure database backups

## Contributing

1. Create a feature branch
2. Make your changes
3. Write/update tests
4. Submit a pull request

## License

MIT License

## Support

For issues and feature requests, please create an issue in the repository.

---

**Developed with ❤️ for seamless e-commerce**
