# Restaurant API Documentation

# Description

This is a comprehensive REST API for a restaurant management system built with Django and Django REST Framework. The API provides functionality to manage users, roles (Customer, Delivery Staff, Manager, System Administrator), food items, categories, shopping carts, and customer orders. Every API endpoint includes authorization and permission constraints, as well as pagination, filtering, and search capabilities.

## Project Structure

This project consists mainly of two apps: **littlelemon** and **api**.

**littlelemon app**

This app contains the model definitions that create the entity relationships required by the API app. The main models include:
- `FoodItem` - Represents menu items with name, cost, and featured status
- `FoodCategory` - Categories for organizing food items
- `CartItem` - Individual items in a customer's shopping cart
- `ShoppingCart` - Customer shopping cart containing cart items
- `CustomerOrder` - Customer orders with delivery tracking
- `Transaction` - Purchase transactions linked to orders
- `TransactionItem` - Individual items within a transaction

**api app**

This app contains the URL dispatchers (routers), serializers, and views for every endpoint of the API. Additionally, it contains helper mixin classes that are inherited by class-based views for common functionality.

**config dir**

This directory contains the configuration files of the project, including the `settings.py` file and the `urls.py` file which contains the main URL dispatchers.

## Installation

### Prerequisites

- Python 3.10 or higher
- pip or pipenv for package management

### Setup Instructions

**1. Clone or navigate to the repository**

```bash
cd littlelemon-API
```

**2. Create a virtual environment**

```bash
# Using venv
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

**3. Install dependencies**

```bash
pip install django djangorestframework django-filter djangorestframework-simplejwt django-environ psycopg2-binary
```

Or if using pipenv:

```bash
pipenv install
```

**Note**: This project includes [Djoser](https://djoser.readthedocs.io/en/latest/introduction.html) as a local app within the repository to avoid compatibility issues with the latest version of Django REST Framework.

### Database Setup

The project supports both PostgreSQL and SQLite databases. By default, it will use SQLite if PostgreSQL environment variables are not configured.

#### Option 1: SQLite (Default - For Development/Testing)

No configuration needed! The project will automatically use SQLite if PostgreSQL environment variables are not set.

#### Option 2: PostgreSQL (For Production)

**Create the environment variables file (.env)**

In the `config/` directory, create a `.env` file with the following:

```env
DEBUG=True
DATABASE_NAME=your_database_name
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USER=your_database_user
DATABASE_PASSWORD=your_database_password
```

**PostgreSQL Setup Steps**

1. Enter the PostgreSQL prompt:
```sql
psql -U postgres -d postgres
```

2. Create the database:
```sql
CREATE DATABASE your_database_name;
```

3. Create the user:
```sql
CREATE USER your_database_user WITH ENCRYPTED PASSWORD 'your_database_password';
```

4. Modify connection parameters:
```sql
ALTER ROLE your_database_user SET client_encoding TO 'utf8';
ALTER ROLE your_database_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE your_database_user SET timezone TO 'UTC';
```

5. Grant permissions:
```sql
GRANT ALL PRIVILEGES ON DATABASE your_database_name TO your_database_user;
```

6. Exit:
```sql
\q
```

### Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Create Superuser

```bash
python manage.py createsuperuser
```

Or use the provided script:
```bash
python -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')"
```

### Run the Server

**Option 1: Use the provided startup script**

```bash
# Windows
start_server.bat

# PowerShell
.\start_server.ps1
```

**Option 2: Manual start**

```bash
python manage.py runserver
```

The server will be available at:
- API Root: http://127.0.0.1:8000/api/
- Admin Panel: http://127.0.0.1:8000/admin/
- Browsable API: http://127.0.0.1:8000/api/

## Quick Start

1. **Activate virtual environment**
   ```bash
   venv\Scripts\activate  # Windows
   ```

2. **Run migrations**
   ```bash
   python manage.py migrate
   ```

3. **Start server**
   ```bash
   python manage.py runserver
   ```

4. **Access the API**
   - Open http://127.0.0.1:8000/api/ in your browser
   - Login at http://127.0.0.1:8000/api/token/login/

## API Endpoints and Usage

The API supports filtering, searching, and ordering for most endpoints. Examples are provided using curl, but you can use any HTTP client.

### Filtering, Searching, and Ordering

**Filtering** (exact match):
```bash
curl -X GET "http://127.0.0.1:8000/api/menu-items?name=Pizza" \
   -H "Content-Type: application/json" \
   -H "Authorization: Bearer {token}"
```

**Searching** (partial match, case-insensitive):
```bash
curl -X GET "http://127.0.0.1:8000/api/menu-items?search=pizza" \
   -H "Content-Type: application/json" \
   -H "Authorization: Bearer {token}"
```

**Ordering**:
```bash
curl -X GET "http://127.0.0.1:8000/api/menu-items?ordering=cost,name" \
   -H "Content-Type: application/json" \
   -H "Authorization: Bearer {token}"
```

**Combined**:
```bash
curl -X GET "http://127.0.0.1:8000/api/menu-items?category=1&search=pizza&ordering=-cost,name" \
   -H "Content-Type: application/json" \
   -H "Authorization: Bearer {token}"
```

## User Roles

| ROLE | GROUP | RESTRICTIONS |
| --- | --- | --- |
| Unauthenticated | None | YES - Limited access |
| Customer | Customer | YES - Own data only |
| Delivery Staff | Delivery Crew | YES - Assigned orders only |
| Manager | Manager | YES - Cannot manage admins |
| System Administrator | SysAdmin | NO - Full access |

## Authentication

### JWT Token Login

**Endpoint**: `/api/token/login/`

```bash
curl -X POST http://127.0.0.1:8000/api/token/login/ \
   -H "Content-Type: application/json" \
   -d '{"username": "your_username", "password": "your_password"}'
```

**Response**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Refresh Token

**Endpoint**: `/api/token/refresh/`

```bash
curl -X POST http://127.0.0.1:8000/api/token/refresh/ \
   -H "Content-Type: application/json" \
   -d '{"refresh": "your_refresh_token"}'
```

## Main API Endpoints

### Users

**GET/POST** `/api/users`
- **GET**: Retrieve list of users (Manager/Admin only)
- **POST**: Create new user (Unauthenticated/Manager/Admin)
- **Filtering**: `username`, `first_name`, `last_name`
- **Searching**: `username`, `first_name`, `last_name`

**GET/PATCH/DELETE** `/api/users/{userId}`
- Retrieve, update, or delete user account

### Food Items

**GET/POST** `/api/menu-items`
- **GET**: Retrieve list of food items (All authenticated users)
- **POST**: Create new food item (Manager/Admin only)
- **Fields**: `name`, `cost`, `is_featured`, `food_category_id`
- **Filtering**: `name`, `cost`, `is_featured`, `category`
- **Searching**: `name`, `cost`, `is_featured`

**Example POST**:
```bash
curl -X POST http://127.0.0.1:8000/api/menu-items \
   -H "Content-Type: application/json" \
   -H "Authorization: Bearer {token}" \
   -d '{
     "name": "Margherita Pizza",
     "cost": "12.99",
     "is_featured": true,
     "food_category_id": 1
   }'
```

**GET/PATCH/DELETE** `/api/menu-items/{itemId}`
- Retrieve, update, or delete specific food item

### Categories

**GET/POST** `/api/categories`
- **GET**: Retrieve list of categories (All authenticated users)
- **POST**: Create new category (Manager/Admin only)
- **Fields**: `name`, `category_slug`
- **Filtering**: `name`, `category_slug`
- **Searching**: `name`, `category_slug`

**GET/PATCH/DELETE** `/api/categories/{categoryId}`
- Retrieve, update, or delete specific category

**GET** `/api/categories/{categoryId}/menu-items`
- Retrieve all food items in a specific category

### Cart Items

**GET/POST** `/api/order-items`
- **GET**: Retrieve user's cart items
- **POST**: Add item to cart
- **Fields**: `id` (food item ID), `quantity`
- **Note**: Automatically sets the current user as the customer

**GET/PATCH/DELETE** `/api/order-items/{itemId}`
- Retrieve, update quantity, or remove cart item

### Shopping Cart

**GET/POST/DELETE** `/api/cart`
- **GET**: Retrieve user's shopping cart
- **POST**: Add cart item to shopping cart (requires cart item ID)
- **DELETE**: Remove item from cart (provide `id`) or clear entire cart (no `id`)

**Example**:
```bash
# Get cart
curl -X GET http://127.0.0.1:8000/api/cart \
   -H "Authorization: Bearer {token}"

# Add item to cart
curl -X POST http://127.0.0.1:8000/api/cart \
   -H "Content-Type: application/json" \
   -H "Authorization: Bearer {token}" \
   -d '{"id": 1}'

# Clear cart
curl -X DELETE http://127.0.0.1:8000/api/cart \
   -H "Authorization: Bearer {token}"
```

### Customer Orders

**GET/POST** `/api/orders`
- **GET**: Retrieve orders (filtered by role)
  - Customers: Own orders only
  - Delivery Staff: Assigned orders only
  - Managers/Admins: All orders
- **POST**: Create order from shopping cart (Customer only)
- **Filtering**: `customer`, `assigned_delivery_person`, `is_delivered`, `order_date`

**GET/PATCH/DELETE** `/api/orders/{orderId}`
- **GET**: Retrieve order details
- **PATCH**: Update order status or assign delivery person
  - Delivery Staff: Can update `status` (0 or 1)
  - Managers: Can update `status` and `assigned_delivery_person_id`
- **DELETE**: Delete order (Manager/Admin only)

**Example PATCH**:
```bash
curl -X PATCH http://127.0.0.1:8000/api/orders/1 \
   -H "Content-Type: application/json" \
   -H "Authorization: Bearer {token}" \
   -d '{"status": 1}'
```

### Transactions

**GET** `/api/purchases`
- Retrieve transaction history
- **Filtering**: `customer`, `transaction_date`
- Customers see only their own transactions

**GET/DELETE** `/api/purchases/{transactionId}`
- Retrieve or delete specific transaction

### Transaction Items

**GET** `/api/purchase-items`
- Retrieve transaction items
- **Filtering**: `customer`, `food_item`, `item_total_price`

**GET/PATCH/DELETE** `/api/purchase-items/{itemId}`
- Retrieve, update, or delete transaction item

## User Groups Management

### Groups

**GET/POST** `/api/groups`
- List or create user groups (Manager/Admin)

**GET/PATCH/DELETE** `/api/groups/{groupId}`
- Manage specific group

### Group Members

**GET/POST** `/api/groups/customers`
- List customers or add user to Customer group

**GET/POST** `/api/groups/delivery-crew`
- List delivery staff or add user to Delivery Crew group

**GET/POST** `/api/groups/managers`
- List managers or add user to Manager group

**GET/POST** `/api/groups/admins`
- List administrators or add user to SysAdmin group (Admin only)

**Example - Add user to group**:
```bash
curl -X POST http://127.0.0.1:8000/api/groups/customers \
   -H "Content-Type: application/json" \
   -H "Authorization: Bearer {token}" \
   -d '{"id": 2}'
```

## Testing

Run the test script to verify setup:

```bash
python test_server.py
```

This will check:
- Model imports
- View imports
- URL configuration
- Database connection
- Superuser existence

## Project Features

- ✅ JWT Authentication
- ✅ Role-based access control
- ✅ Pagination (5 items per page)
- ✅ Filtering, searching, and ordering
- ✅ Shopping cart functionality
- ✅ Order management
- ✅ Transaction tracking
- ✅ Browsable API interface
- ✅ Admin panel integration

## Technology Stack

- **Django** - Web framework
- **Django REST Framework** - API framework
- **Django REST Framework Simple JWT** - JWT authentication
- **Django Filter** - Advanced filtering
- **Djoser** - User management (included as local app)
- **PostgreSQL/SQLite** - Database

## License

This project is for educational purposes.

## Support

For issues or questions, please refer to the Django REST Framework documentation or Django documentation.
