# Setup & Deployment Guide

## Quick Start

### 1. Initial Setup

```bash
# Navigate to project
cd bookstore_project

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Database

#### Option A: PostgreSQL (Recommended)

```bash
# Install PostgreSQL
# Windows: Download from https://www.postgresql.org/download/windows/
# Mac: brew install postgresql
# Linux: sudo apt-get install postgresql

# Create database and user
createdb online_bookstore
# Or use pgAdmin GUI

# Update .env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=online_bookstore
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

#### Option B: SQLite (Development Only)

```bash
# .env will use default SQLite if not configured
# Keep defaults or update to:
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

### 3. Environment Setup

```bash
# Copy example .env
cp .env.example .env

# Edit .env with your settings
# Key values to change:
# - SECRET_KEY: Generate using: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
# - DB credentials (if using PostgreSQL)
# - JWT_SECRET_KEY
# - CORS_ALLOWED_ORIGINS
# - EMAIL settings (if needed)
```

### 4. Database Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser
# Then enter:
# Username: admin
# Email: admin@example.com
# Password: (enter secure password)

# Load sample data (optional)
python manage.py loaddata sample_data.json  # If available
```

### 5. Run Development Server

```bash
# Start development server
python manage.py runserver

# Server will be available at:
# http://localhost:8000
# Admin panel: http://localhost:8000/admin
```

## Testing the API

### Using cURL

```bash
# 1. Register User
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "phone": "+919876543210",
    "password": "TestPassword123",
    "password_confirm": "TestPassword123"
  }'

# Response includes token:
# {"token": "eyJ0eXAiOiJKV1QiLCJhbGc...", "user": {...}}

# 2. Save token for authenticated requests
TOKEN="your_token_here"

# 3. Get User Profile
curl -X GET http://localhost:8000/api/v1/auth/profile/ \
  -H "Authorization: Bearer $TOKEN"

# 4. Add Address
curl -X POST http://localhost:8000/api/v1/auth/addresses/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "full_name": "John Doe",
    "phone": "+919876543210",
    "house_no": "123",
    "street": "Main Street",
    "city": "New York",
    "state": "NY",
    "pincode": "10001",
    "country": "USA"
  }'

# 5. Create Category (Admin)
curl -X POST http://localhost:8000/api/v1/catalog/categories/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "category_name": "Python Books",
    "description": "Books about Python Programming"
  }'

# 6. Create Product (Admin)
curl -X POST http://localhost:8000/api/v1/catalog/products/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "category": 1,
    "name": "Python Crash Course",
    "author": "Eric Matthes",
    "description": "A hands-on introduction to programming",
    "price": "29.99",
    "stock": 100,
    "is_active": true
  }'

# 7. List Products
curl -X GET "http://localhost:8000/api/v1/catalog/products/?page=1&page_size=10" \
  -H "Content-Type: application/json"

# 8. Get Product Detail
curl -X GET "http://localhost:8000/api/v1/catalog/products/detail/?product_id=1" \
  -H "Content-Type: application/json"

# 9. Add to Cart
curl -X POST http://localhost:8000/api/v1/cart/add-item/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "product": 1,
    "quantity": 2
  }'

# 10. Get Cart
curl -X GET http://localhost:8000/api/v1/cart/ \
  -H "Authorization: Bearer $TOKEN"

# 11. Checkout (Create Order)
curl -X POST http://localhost:8000/api/v1/orders/checkout/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "address_id": 1
  }'

# 12. Get Orders
curl -X GET http://localhost:8000/api/v1/orders/?page=1 \
  -H "Authorization: Bearer $TOKEN"

# 13. Create Payment
curl -X POST http://localhost:8000/api/v1/payments/create/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "order": 1,
    "payment_method": "credit_card",
    "amount": "59.98"
  }'

# 14. Update Payment Status
curl -X PUT http://localhost:8000/api/v1/payments/update/?payment_id=1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "payment_status": "completed",
    "transaction_id": "TXN12345"
  }'

# 15. Add to Wishlist
curl -X POST http://localhost:8000/api/v1/wishlist/add/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "product": 1
  }'

# 16. Get Wishlist
curl -X GET http://localhost:8000/api/v1/wishlist/?page=1 \
  -H "Authorization: Bearer $TOKEN"
```

### Using Postman

1. **Import Collection**: Create requests manually or import from OpenAPI spec
2. **Set Environment Variables**:
   - `BASE_URL`: http://localhost:8000
   - `TOKEN`: Your JWT token
3. **Create Requests**: Use the endpoints listed in README.md

## Admin Panel

1. Navigate to `http://localhost:8000/admin`
2. Login with superuser credentials
3. Manage all app resources

## Troubleshooting

### PostgreSQL Connection Error
```
Error: could not connect to database server
Solution:
1. Verify PostgreSQL is running
2. Check DB_HOST, DB_PORT, DB_USER, DB_PASSWORD in .env
3. Ensure database exists: createdb online_bookstore
```

### Migration Issues
```
Solution:
# Reset migrations (dev only):
python manage.py migrate accounts zero
python manage.py migrate
```

### Port Already in Use
```
# Run on different port:
python manage.py runserver 8001
```

### Import Errors
```
Solution:
# Reinstall packages:
pip install -r requirements.txt --force-reinstall
```

## Production Deployment

### Using Gunicorn

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn config.wsgi --bind 0.0.0.0:8000

# Production settings:
# - DEBUG = False
# - ALLOWED_HOSTS = ['yourdomain.com']
# - Use strong SECRET_KEY
```

### Using Docker (Optional)

```dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "config.wsgi", "--bind", "0.0.0.0:8000"]
```

```bash
# Build and run
docker build -t bookstore-api .
docker run -p 8000:8000 bookstore-api
```

### Using Nginx

```nginx
upstream bookstore {
    server localhost:8000;
}

server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://bookstore;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/staticfiles/;
    }

    location /media/ {
        alias /path/to/media/;
    }
}
```

## Useful Commands

```bash
# Create app migrations
python manage.py makemigrations accounts

# Apply specific migrations
python manage.py migrate accounts

# Show SQL for migrations
python manage.py sqlmigrate accounts 0001

# Shell access
python manage.py shell

# Create test data
python manage.py shell < scripts/create_test_data.py

# Backup database
pg_dump online_bookstore > backup.sql

# Restore database
psql online_bookstore < backup.sql

# Run tests
python manage.py test

# Check code quality
pip install flake8
flake8 .

# Format code
pip install black
black .

# Type checking
pip install mypy
mypy .
```

## Next Steps

1. ✅ Setup project locally
2. ✅ Test API endpoints
3. ✅ Configure frontend CORS
4. ✅ Set up payment gateway integration
5. ✅ Add email notifications
6. ✅ Implement password reset
7. ✅ Add order tracking
8. ✅ Deploy to production

For more information, see README.md
