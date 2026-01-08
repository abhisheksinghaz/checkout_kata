# Supermarket Checkout System - Complete Architecture Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Diagrams](#architecture-diagrams)
3. [API Documentation](#api-documentation)
4. [Data Flow](#data-flow)
5. [Use Cases](#use-cases)
6. [Deployment Guide](#deployment-guide)

---

## System Overview

The Supermarket Checkout System is a comprehensive Django REST API application that manages products, promotions, shopping carts, and checkout processes for a supermarket. The system is built using the MVC (Model-View-Controller) architecture pattern with Django REST Framework.

### Key Features
- ✅ Product Management (CRUD operations)
- ✅ Dynamic Promotion System (5 types of promotions)
- ✅ Session-based Shopping Cart
- ✅ Real-time Price Calculation with Promotions
- ✅ RESTful API with full CRUD support
- ✅ Extensible promotion engine
- ✅ Database-driven configuration

### Technology Stack
- **Backend Framework**: Django 5.0 + Django REST Framework 3.14
- **Database**: SQLite (Dev) / PostgreSQL (Production)
- **Caching**: Redis
- **API**: RESTful JSON API
- **Authentication**: Session-based
- **Admin Interface**: Django Admin

---

## Architecture Diagrams

### 1. High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                         |
│  Web Browser │ Mobile App │ POS Terminal │ API Clients      │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS/REST
┌──────────────────────────▼─────────────────────────────────┐
│                      API LAYER (Django)                    │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Products   │  │  Promotions  │  │   Checkout   │       │
│  │     API     │  │      API     │  │      API     │       │
│  └─────────────┘  └──────────────┘  └──────────────┘       │
└──────────────────────────┬─────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                      │
│  ┌─────────────────────────┐  ┌──────────────────────────┐  │
│  │   CheckoutService       │  │   PricingEngine          │  │
│  │  - Cart Management      │  │  - Bulk Discount         │  │
│  │  - Total Calculation    │  │  - Buy X Get Y Free      │  │
│  │                         │  │  - Percentage Off        │  │
│  │                         │  │  - Fixed Discount        │  │
│  │                         │  │  - Tiered Pricing        │  │
│  └─────────────────────────┘  └──────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────────┐
│                     DATA ACCESS LAYER                      │
│  ┌──────────┐ ┌───────────┐ ┌──────┐ ┌──────────┐          │
│  │ Product  │ │ Promotion │ │ Cart │ │ CartItem │          │
│  │  Model   │ │   Model   │ │Model │ │  Model   │          │
│  └──────────┘ └───────────┘ └──────┘ └──────────┘          │
└──────────────────────────┬─────────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────────┐
│                      DATABASE LAYER                        │
│                 PostgreSQL / SQLite                        │
│  ┌──────────┐ ┌───────────┐ ┌──────┐ ┌──────────┐          │
│  │ products │ │promotions │ │carts │ │cart_items│          │
│  └──────────┘ └───────────┘ └──────┘ └──────────┘          │
└────────────────────────────────────────────────────────────┘
```

---

## API Documentation

### Base URL
```
http://localhost:8000/api/
```

### API Endpoints Summary

#### Product APIs (6 endpoints)
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/products/` | List all products | No |
| POST | `/products/` | Create new product | Admin |
| GET | `/products/:id/` | Get product details | No |
| PUT | `/products/:id/` | Update product | Admin |
| DELETE | `/products/:id/` | Delete product | Admin |
| GET | `/products/:id/promotions/` | Get product promotions | No |

#### Promotion APIs (6 endpoints)
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/promotions/` | List all promotions | No |
| POST | `/promotions/` | Create promotion | Admin |
| GET | `/promotions/:id/` | Get promotion details | No |
| PUT | `/promotions/:id/` | Update promotion | Admin |
| POST | `/promotions/:id/deactivate/` | Deactivate promotion | Admin |
| POST | `/promotions/:id/activate/` | Activate promotion | Admin |

#### Checkout APIs (5 endpoints)
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/checkout/` | Get current cart | Session |
| POST | `/checkout/scan/` | Add item to cart | Session |
| POST | `/checkout/remove/` | Remove item | Session |
| GET | `/checkout/calculate/` | Calculate total | Session |
| POST | `/checkout/clear/` | Clear cart | Session |

---

## Data Flow

### Complete Checkout Flow (B → A → B → Calculate)

```
STEP 1: Scan Item B
User → API → Controller → Service → Database
         ↓
[POST /checkout/scan/ {product_id: "B"}]
         ↓
CheckoutAPIView.scan()
         ↓
CheckoutService.get_or_create_cart(session_id)
         ↓
Product.objects.get(product_id="B")
         ↓
CartItem.objects.create(cart=cart, product=B)
         ↓
Response: {success: true, cart_total_items: 1}

STEP 2: Scan Item A
[Similar flow, adds A to cart]
Response: {success: true, cart_total_items: 2}

STEP 3: Scan Item B (again)
[Similar flow, adds second B to cart]
Response: {success: true, cart_total_items: 3}

STEP 4: Calculate Total
User → API → Controller → Service → PricingEngine → Database
         ↓
[GET /checkout/calculate/]
         ↓
CheckoutService.calculate_cart_total(cart)
         ↓
cart.get_item_counts() → {B: 2, A: 1}
         ↓
For Product B (quantity: 2):
  ├─ Get Product B details
  ├─ Get Active Promotions for B
  │  └─ Found: bulk_discount {quantity: 2, price: 45}
  ├─ PricingEngine.calculate_price()
  │  └─ _calculate_bulk_discount()
  │     ├─ special_sets = 2 // 2 = 1
  │     ├─ remaining = 2 % 2 = 0
  │     └─ total = (1 × 45) + (0 × 30) = 45
  └─ Subtotal: Rs 45, Savings: Rs 15

For Product A (quantity: 1):
  ├─ Get Product A details
  ├─ Get Active Promotions for A
  │  └─ Found: bulk_discount {quantity: 3, price: 130}
  ├─ PricingEngine.calculate_price()
  │  └─ _calculate_bulk_discount()
  │     ├─ special_sets = 1 // 3 = 0 (not enough for discount)
  │     ├─ remaining = 1 % 3 = 1
  │     └─ total = (0 × 130) + (1 × 50) = 50
  └─ Subtotal: Rs 50, Savings: Rs 0

Final Result:
  ├─ Total: Rs 95
  ├─ Item Count: 3
  ├─ Total Savings: Rs 15
  └─ Breakdown:
     ├─ B × 2: Rs 45 (saved Rs 15)
     └─ A × 1: Rs 50 (saved Rs 0)
```

---

## Use Cases

### Primary Actors
1. **Customer** - Shops and checks out
2. **Cashier** - Processes customer purchases
3. **Store Admin** - Manages products and promotions

### Use Case Scenarios

#### UC1: Customer Scans Items and Checks Out
```
Actor: Customer
Preconditions: Products exist in system
Main Flow:
  1. Customer scans product B
  2. System adds B to cart (1 item)
  3. Customer scans product A
  4. System adds A to cart (2 items)
  5. Customer scans product B again
  6. System adds B to cart (3 items)
  7. Customer requests total
  8. System calculates: Rs 95 (saved Rs 15)
  9. Customer completes purchase
Postconditions: Cart is cleared, purchase recorded
```

#### UC2: Admin Creates Time-Limited Promotion
```
Actor: Store Admin
Preconditions: Product exists
Main Flow:
  1. Admin navigates to promotion creation
  2. Admin selects product A
  3. Admin chooses "Bulk Discount" type
  4. Admin sets quantity: 3, price: 130
  5. Admin sets start date: 2026-01-08
  6. Admin sets end date: 2026-02-08
  7. Admin sets priority: 1
  8. System validates and creates promotion
Postconditions: Promotion is active and applied to purchases
```

#### UC3: System Applies Multiple Promotions
```
Actor: System (Automatic)
Trigger: Customer requests total calculation
Main Flow:
  1. System gets all items in cart
  2. System groups items by product
  3. For each product:
     a. Get all active promotions
     b. Sort by priority (highest first)
     c. Apply highest priority promotion
     d. Calculate discounted price
  4. System sums all subtotals
  5. System calculates total savings
  6. System returns breakdown to customer
Result: Best possible price for customer
```

---

## Promotion Types Explained

### 1. Bulk Discount
**Configuration:**
```json
{
  "promotion_type": "bulk_discount",
  "promotion_data": {
    "quantity": 3,
    "price": 130
  }
}
```
**Example:** Buy 3 Apples for Rs 130 (instead of Rs 150)
**Algorithm:**
```
special_sets = quantity ÷ required_quantity
remaining = quantity % required_quantity
total = (special_sets × special_price) + (remaining × unit_price)
```

### 2. Buy X Get Y Free
**Configuration:**
```json
{
  "promotion_type": "buy_x_get_y_free",
  "promotion_data": {
    "buy_quantity": 2,
    "free_quantity": 1
  }
}
```
**Example:** Buy 2 Cherries, Get 1 Free
**Algorithm:**
```
deal_size = buy_quantity + free_quantity
full_deals = quantity ÷ deal_size
remaining = quantity % deal_size
items_to_pay = (full_deals × buy_quantity) + remaining
total = items_to_pay × unit_price
```

### 3. Percentage Off
**Configuration:**
```json
{
  "promotion_type": "percentage_off",
  "promotion_data": {
    "min_quantity": 5,
    "discount_percent": 20
  }
}
```
**Example:** 20% off when buying 5 or more Dates
**Algorithm:**
```
if quantity >= min_quantity:
    total = quantity × unit_price × (1 - discount_percent/100)
else:
    total = quantity × unit_price
```

### 4. Fixed Discount
**Configuration:**
```json
{
  "promotion_type": "fixed_discount",
  "promotion_data": {
    "min_quantity": 1,
    "discount_amount": 5
  }
}
```
**Example:** Rs 5 off per item
**Algorithm:**
```
if quantity >= min_quantity:
    discounted_price = max(0, unit_price - discount_amount)
    total = quantity × discounted_price
```

### 5. Tiered Pricing
**Configuration:**
```json
{
  "promotion_type": "tiered_pricing",
  "promotion_data": {
    "tiers": [
      [1, 10],   // 1-4 items: Rs 10 each
      [5, 9],    // 5-9 items: Rs 9 each
      [10, 8]    // 10+ items: Rs 8 each
    ]
  }
}
```
**Example:** Volume-based pricing for Elderberries
**Algorithm:**
```
for each tier (sorted highest to lowest):
    if quantity >= tier_min_quantity:
        total = quantity × tier_price
        break
```

---

## Database Schema

### Products Table
```sql
CREATE TABLE products (
    product_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL CHECK (unit_price >= 0),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Promotions Table
```sql
CREATE TABLE promotions (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(10) REFERENCES products(product_id),
    promotion_type VARCHAR(20) NOT NULL,
    promotion_data JSONB NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    priority INTEGER DEFAULT 1,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_product_active (product_id, active, start_date, end_date)
);
```

### Carts Table
```sql
CREATE TABLE carts (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Cart Items Table
```sql
CREATE TABLE cart_items (
    id SERIAL PRIMARY KEY,
    cart_id INTEGER REFERENCES carts(id) ON DELETE CASCADE,
    product_id VARCHAR(10) REFERENCES products(product_id),
    added_at TIMESTAMP DEFAULT NOW()
);
```

---

## Deployment Guide

### Development Environment
```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Initialize
python manage.py makemigrations
python manage.py migrate
python manage.py load_sample_data
python manage.py createsuperuser

# Run
python manage.py runserver
```

### Production Environment
```bash
# Install production dependencies
pip install gunicorn psycopg2-binary

# Configure PostgreSQL
DATABASE_URL=postgresql://user:pass@localhost:5432/supermarket_db

# Collect static files
python manage.py collectstatic --noinput

# Run with Gunicorn
gunicorn supermarket_api.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --threads 2 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -
```

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name api.supermarket.com;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static/ {
        alias /var/www/supermarket/static/;
    }
}
```

---

## Testing Examples

### Example Test Cases

#### Test 1: Basic Checkout (B, A, B)
```bash
# Scan B
curl -X POST http://localhost:8000/api/checkout/scan/ \
  -H "Content-Type: application/json" \
  -d '{"product_id": "B"}' \
  --cookie-jar cookies.txt

# Scan A
curl -X POST http://localhost:8000/api/checkout/scan/ \
  -H "Content-Type: application/json" \
  -d '{"product_id": "A"}' \
  --cookie cookies.txt --cookie-jar cookies.txt

# Scan B again
curl -X POST http://localhost:8000/api/checkout/scan/ \
  -H "Content-Type: application/json" \
  -d '{"product_id": "B"}' \
  --cookie cookies.txt --cookie-jar cookies.txt

# Calculate total
curl -X GET http://localhost:8000/api/checkout/calculate/ \
  --cookie cookies.txt

# Expected: Total = Rs 95, Savings = Rs 15
```

#### Test 2: Create and Apply Promotion
```bash
# Create promotion
curl -X POST http://localhost:8000/api/promotions/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "C",
    "promotion_type": "buy_x_get_y_free",
    "promotion_data": {"buy_quantity": 2, "free_quantity": 1},
    "start_date": "2026-01-08T00:00:00Z",
    "priority": 1
  }'

# Test promotion (buy 3, pay for 2)
curl -X POST http://localhost:8000/api/checkout/scan/ \
  -d '{"product_id": "C"}' --cookie-jar cookies2.txt
curl -X POST http://localhost:8000/api/checkout/scan/ \
  -d '{"product_id": "C"}' --cookie cookies2.txt --cookie-jar cookies2.txt
curl -X POST http://localhost:8000/api/checkout/scan/ \
  -d '{"product_id": "C"}' --cookie cookies2.txt --cookie-jar cookies2.txt

curl -X GET http://localhost:8000/api/checkout/calculate/ \
  --cookie cookies2.txt

# Expected: 3 items, pay for 2 only (Rs 40 instead of Rs 60)
```

---

## Performance Considerations

### Optimization Strategies

1. **Database Indexing**
   - Index on `(product_id, active, start_date, end_date)` for promotions
   - Index on `session_id` for carts
   - Index on `(cart_id, product_id)` for cart_items

2. **Caching**
   - Cache active promotions (5-minute TTL)
   - Cache product details (15-minute TTL)
   - Session-based cart caching

3. **Query Optimization**
   - Use `select_related()` for foreign keys
   - Use `prefetch_related()` for reverse foreign keys
   - Avoid N+1 queries

4. **Scalability**
   - Horizontal scaling with load balancer
   - Database read replicas
   - Redis for session storage
   - CDN for static assets

---

## Security Considerations

1. **Authentication & Authorization**
   - Session-based auth for customers
   - Token-based auth for admin operations
   - Role-based access control (RBAC)

2. **Input Validation**
   - DRF serializer validation
   - Database constraints
   - JSON schema validation for promotion_data

3. **SQL Injection Prevention**
   - Django ORM (parameterized queries)
   - Never use raw SQL with user input

4. **CSRF Protection**
   - Django CSRF middleware enabled
   - CSRF token validation

5. **Rate Limiting**
   - API rate limiting (100 requests/minute)
   - Throttling for expensive operations

---

## Monitoring & Logging

### Key Metrics to Monitor
- Request rate (requests/second)
- Response time (avg, p95, p99)
- Error rate (4xx, 5xx)
- Database query time
- Cache hit rate
- Cart abandonment rate
- Promotion usage statistics

### Logging Strategy
```python
import logging

logger = logging.getLogger(__name__)

# Log checkout events
logger.info(f"Checkout calculated: session={session_id}, total={total}")

# Log promotion applications
logger.info(f"Promotion applied: promo_id={promo_id}, savings={savings}")

# Log errors
logger.error(f"Failed to calculate total: {error}", exc_info=True)
```

---

## Future Enhancements

1. **Advanced Features**
   - Multi-store support
   - Inventory management
   - Order history
   - Customer loyalty program
   - Gift cards and vouchers

2. **Promotion Enhancements**
   - Cross-product promotions (Buy A+B together)
   - Time-based promotions (Happy Hour)
   - Customer-segment promotions (VIP only)
   - Stackable promotions

3. **Integration Possibilities**
   - Payment gateway integration
   - Receipt generation (PDF)
   - Email notifications
   - SMS alerts
   - Mobile app push notifications

---

## Conclusion

This comprehensive architecture provides:
- ✅ Scalable REST API design
- ✅ Flexible promotion system
- ✅ Clean separation of concerns
- ✅ Easy to maintain and extend
- ✅ Production-ready deployment
- ✅ Comprehensive testing coverage

The system is designed to handle real-world supermarket operations with high performance, reliability, and extensibility.
