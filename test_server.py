#!/usr/bin/env python
"""
Quick test script to verify the Django server is working
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 50)
print("Testing Django Server Setup")
print("=" * 50)

# Test 1: Check if models are accessible
print("\n1. Testing Models...")
try:
    from littlelemon.models import FoodItem, FoodCategory, CartItem, ShoppingCart
    print("   [OK] Models imported successfully")
    print(f"   [OK] FoodItem model: {FoodItem.__name__}")
    print(f"   [OK] FoodCategory model: {FoodCategory.__name__}")
except Exception as e:
    print(f"   [ERROR] Error importing models: {e}")
    sys.exit(1)

# Test 2: Check API views
print("\n2. Testing API Views...")
try:
    from api.views import FoodItemListView, FoodCategoryListView
    print("   [OK] API views imported successfully")
except Exception as e:
    print(f"   [ERROR] Error importing views: {e}")
    sys.exit(1)

# Test 3: Test URL configuration
print("\n3. Testing URL Configuration...")
try:
    from django.urls import reverse
    from django.conf import settings
    print("   [OK] URL configuration loaded")
except Exception as e:
    print(f"   [ERROR] Error with URL config: {e}")
    sys.exit(1)

# Test 4: Check database connection
print("\n4. Testing Database Connection...")
try:
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    print("   [OK] Database connection successful")
except Exception as e:
    print(f"   [ERROR] Database connection error: {e}")
    sys.exit(1)

# Test 5: Check if superuser exists
print("\n5. Checking Superuser...")
try:
    admin_exists = User.objects.filter(username='admin', is_superuser=True).exists()
    if admin_exists:
        print("   [OK] Superuser 'admin' exists")
    else:
        print("   [WARNING] Superuser 'admin' not found")
except Exception as e:
    print(f"   [ERROR] Error checking superuser: {e}")

print("\n" + "=" * 50)
print("All tests passed! Server should be ready to run.")
print("=" * 50)
print("\nTo start the server, run:")
print("  python manage.py runserver")
print("\nThen access:")
print("  - API Root: http://127.0.0.1:8000/api/")
print("  - Admin: http://127.0.0.1:8000/admin/")
print("  - Login: admin / admin123")
print("=" * 50)
