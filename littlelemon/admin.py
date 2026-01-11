from django.contrib import admin
from .models import (
    FoodItem, FoodCategory, ShoppingCart, CustomerOrder, CartItem, Transaction, TransactionItem,
)

@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'cost', 'is_featured', 'food_category']
    list_filter = ['is_featured', 'food_category']
    search_fields = ['name']

@admin.register(FoodCategory)
class FoodCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_slug']
    search_fields = ['name']

@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ['customer', 'get_item_count']
    search_fields = ['customer__username']
    
    def get_item_count(self, obj):
        return obj.cart_items.count()
    get_item_count.short_description = 'Items'

@admin.register(CustomerOrder)
class CustomerOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'order_total', 'is_delivered', 'order_date']
    list_filter = ['is_delivered', 'order_date']
    search_fields = ['customer__username']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['customer', 'food_item', 'item_quantity', 'item_total_price']
    search_fields = ['customer__username', 'food_item__name']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'transaction_date']
    search_fields = ['customer__username']

@admin.register(TransactionItem)
class TransactionItemAdmin(admin.ModelAdmin):
    list_display = ['customer', 'food_item', 'item_quantity', 'item_total_price']
    search_fields = ['customer__username', 'food_item__name']