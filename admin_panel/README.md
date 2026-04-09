# BookNest Admin Panel Documentation

## 📋 Overview

The BookNest Admin Panel is a fully functional, production-ready dashboard built with Django and Bootstrap 5. It provides administrators with comprehensive tools to manage all aspects of the BookNest e-commerce platform.

---

## ✨ Features

### 1. **Admin Dashboard**
- Summary statistics (Total Users, Products, Orders, Revenue)
- Recent orders display
- Quick access links
- Low stock alerts
- Payment statistics

### 2. **User Management**
- View all users with pagination
- Search users by name or email
- View detailed user information
- Delete users (with cascade deletion of related data)
- User role display (Admin/Regular)

### 3. **Product Management (CRUD)**
- Add new products
- Edit existing products
- Delete products
- Search products by name or author
- Pagination support
- Stock level indicators
- Category management

### 4. **Order Management**
- View all orders with full details
- Filter orders by status (Pending, Shipped, Out for Delivery, Delivered, Cancelled)
- Update order status
- View order items and calculations
- Track order timestamps

### 5. **Payment Management**
- View all payment records
- Filter payments by status (Success/Failed)
- Track transaction details
- Payment amount and timestamps

### 6. **Cart & Wishlist (Read-Only)**
- View user carts with items
- View user wishlists
- Read-only access (no modifications required)
- Pagination for large datasets

### 7. **Security**
- Session-based authentication
- Admin-only access control
- Password hashing (SHA-256)
- CSRF protection
- Secure logout

---

## 🚀 Installation & Setup

### Step 1: Verify Admin App is Installed

The admin panel app should already be included in your Django installation. Verify it's in `INSTALLED_APPS`:

```python
# booknest/settings.py
INSTALLED_APPS = [
    ...
    "admin_panel",
    ...
]
```

### Step 2: Create an Admin User

Use the Django management command to create your first admin user:

```bash
python manage.py create_admin \
  --email admin@booknest.com \
  --username admin \
  --password your_secure_password \
  --phone "+91-XXXXXXXX"
```

**Example:**
```bash
python manage.py create_admin \
  --email sarah.admin@booknest.com \
  --username sarah_admin \
  --password AdminPassword123 \
  --phone "+91-9876543210"
```

### Step 3: Access the Admin Panel

1. Navigate to: `http://localhost:8000/admin/login/`
2. Log in with your admin credentials
3. You'll be redirected to the dashboard

---

## 📖 Usage Guide

### Admin Login

**URL:** `http://localhost:8000/admin/login/`

- Enter your registered email and password
- Session will be maintained for 24 hours
- Click "Logout" to end your session

### Dashboard

**URL:** `http://localhost:8000/admin/` or `http://localhost:8000/admin/dashboard/`

The dashboard displays:
- Key metrics (Users, Products, Orders, Revenue)
- Recent orders
- Payment success/failure ratio
- Quick action buttons
- Status indicators

### User Management

**URL:** `http://localhost:8000/admin/users/`

**Features:**
- **List:** View all users with pagination (20 per page)
- **Search:** Type user name or email to filter
- **View Details:** Click "View" to see complete user information
- **Delete:** Permanently remove a user (confirmation required)
  - Deletes: user account, addresses, cart, wishlist, orders

### Product Management

**URL:** `http://localhost:8000/admin/products/`

**Create Product:** `http://localhost:8000/admin/products/add/`
- Book Title (required)
- Author (required)
- Category (required, dropdown from Firebase)
- Price (required, in Rupees)
- Stock Quantity (required)
- Image URL (optional, must be HTTPS)
- Description (optional)

**Edit Product:** `http://localhost:8000/admin/products/<product_id>/edit/`
- All fields except created_at and product_id are editable

**Delete Product:** Click trash icon on product list
- Confirmation required before deletion

### Order Management

**URL:** `http://localhost:8000/admin/orders/`

**Filter Orders:**
- Pending: Awaiting processing
- Shipped: On the way to customer
- Out for Delivery: Final delivery stage
- Delivered: Successfully delivered
- Cancelled: Order cancelled

**Update Order Status:**
1. Click "View" on any order
2. Select new status from dropdown
3. Click "Update Status"
4. Status will be updated immediately

### Payment Management

**URL:** `http://localhost:8000/admin/payments/`

**Filter Payments:**
- All: Show all records
- Successful: Only successful transactions
- Failed: Only failed transactions

**Information Displayed:**
- Payment ID
- Related Order ID
- Amount (₹)
- Payment Status
- Transaction ID (Razorpay)
- Payment Date

### View Carts

**URL:** `http://localhost:8000/admin/carts/`

- View all active shopping carts
- See items in each cart
- View product quantities
- **Read-only:** No modifications available

### View Wishlists

**URL:** `http://localhost:8000/admin/wishlists/`

- View all user wishlists
- See favorited products
- View wishlist owners
- **Read-only:** No modifications available

---

## 🏗️ Project Structure

```
admin_panel/
├── __init__.py
├── apps.py                  # App configuration
├── decorators.py            # Authentication decorators
├── forms.py                 # Django forms
├── services.py              # Firestore business logic
├── views.py                 # View controllers
├── urls.py                  # URL routing
├── management/
│   ├── __init__.py
│   └── commands/
│       ├── __init__.py
│       └── create_admin.py  # Create admin user command
└── templates/
    └── admin/
        ├── base.html        # Main layout template
        ├── login.html       # Login page
        ├── dashboard.html   # Dashboard
        ├── users/
        │   ├── list.html    # User list
        │   └── detail.html  # User details
        ├── products/
        │   ├── list.html    # Product list
        │   └── form.html    # Product form
        ├── orders/
        │   ├── list.html    # Order list
        │   └── detail.html  # Order details
        ├── payments/
        │   └── list.html    # Payment list
        ├── carts/
        │   └── list.html    # Cart list
        └── wishlists/
            └── list.html    # Wishlist list
```

---

## 🔐 Security Features

### Authentication
- Session-based authentication
- Admin users marked with `is_admin: True` in Firestore
- 24-hour session timeout
- CSRF token protection on all forms

### Authorization
- All routes require admin authentication
- Non-admin users are redirected to login
- Automatic session expiration
- Logout clears all session data

### Password Security
- SHA-256 hashing algorithm
- ⚠️ **Note:** For production, upgrade to bcrypt or Argon2

### Best Practices
1. Use strong, unique admin passwords
2. Change default admin credentials
3. Regularly audit admin access
4. Enable HTTPS in production
5. Keep Django and dependencies updated

---

## 🔧 Configuration

### Session Settings

Edit `booknest/settings.py`:

```python
# Session configuration
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False  # Set to True with HTTPS
```

### Pagination

Default: 20 items per page

Edit in `admin_panel/views.py`:
```python
ITEMS_PER_PAGE = 20
```

---

## 🚨 Troubleshooting

### Login Not Working
1. Verify admin user was created correctly
2. Check email and password spelling
3. Ensure user has `is_admin: True` in Firestore
4. Check Django session middleware is enabled

### Templates Not Loading
1. Ensure `django.contrib.staticfiles` is in `INSTALLED_APPS`
2. Verify `APP_DIRS = True` in `TEMPLATES` configuration
3. Run: `python manage.py collectstatic`

### Firestore Connection Issues
1. Verify Firebase credentials file path
2. Check Firestore database is initialized
3. Ensure collections exist in Firestore
4. Check Firebase authentication

### Forms Not Validating
1. Check form field requirements
2. Verify CSRF token is included
3. Check browser console for JavaScript errors
4. Ensure form data meets validation criteria

---

## 📊 API Endpoints Reference

All admin routes are prefixed with `/admin/`:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/admin/login/` | GET/POST | Admin login |
| `/admin/logout/` | GET | Admin logout |
| `/admin/` | GET | Dashboard |
| `/admin/users/` | GET | User list |
| `/admin/users/<id>/` | GET | User details |
| `/admin/users/<id>/delete/` | POST | Delete user |
| `/admin/products/` | GET | Product list |
| `/admin/products/add/` | GET/POST | Create product |
| `/admin/products/<id>/edit/` | GET/POST | Edit product |
| `/admin/products/<id>/delete/` | POST | Delete product |
| `/admin/orders/` | GET | Order list |
| `/admin/orders/<id>/` | GET | Order details |
| `/admin/orders/<id>/update-status/` | POST | Update order status |
| `/admin/payments/` | GET | Payment list |
| `/admin/carts/` | GET | Cart list |
| `/admin/wishlists/` | GET | Wishlist list |

---

## 🎨 UI/UX Features

### Design System
- **Color Scheme:** Professional blue and gray palette
- **Typography:** Segoe UI, clean and readable
- **Icons:** Font Awesome 6.4
- **Framework:** Bootstrap 5.3

### Responsive Design
- Desktop: Full functionality
- Tablet: Optimized layout
- Mobile: Collapsed sidebar, stacked forms
- All tables horizontally scrollable on small screens

### Accessibility
- ARIA labels on interactive elements
- Semantic HTML structure
- Keyboard navigation support
- High contrast text and buttons

---

## 📝 Best Practices

### When Adding New Admin Features
1. Create service methods in `services.py`
2. Add view class in `views.py`
3. Create URL route in `urls.py`
4. Build template in `templates/admin/`
5. Add navigation link in `base.html`
6. Test thoroughly before deployment

### Data Management
1. Always confirm before deleting
2. Implement proper error handling
3. Log important admin actions
4. Regular data backups
5. Monitor Firestore usage

### Performance
1. Pagination for large datasets (default: 20 items)
2. Index frequently searched fields in Firestore
3. Cache statistics on dashboard
4. Minimize Firebase queries per page

---

## 🐛 Reporting Issues

When reporting bugs, include:
1. URL where issue occurred
2. Error message (if any)
3. Steps to reproduce
4. Browser and OS information
5. Screenshots/screen recordings

---

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.3/)
- [Firebase Documentation](https://firebase.google.com/docs)
- [Firestore Best Practices](https://firebase.google.com/docs/firestore/best-practices)

---

## 📄 License

Part of the BookNest project. All rights reserved.

---

## 🤝 Support

For issues or questions:
1. Check this documentation
2. Review the admin panel code comments
3. Check browser console for errors
4. Verify Django/Firebase configuration

---

**Last Updated:** March 2026
**Version:** 1.0
**Status:** Production Ready ✓
