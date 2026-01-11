from rest_framework import serializers
from django.contrib.auth.models import User, Group

from littlelemon.models import (
    FoodItem, FoodCategory, ShoppingCart, CustomerOrder, CartItem, Transaction, TransactionItem,
)


class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']


class AccountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
    

class FoodItemSerializer(serializers.HyperlinkedModelSerializer):
    food_category_id = serializers.IntegerField(write_only=True, source='food_category')

    class Meta:
        model = FoodItem
        fields = ['id', 'name', 'cost', 'is_featured', 'food_category', 'food_category_id']
        read_only_fields = ['food_category']


class FoodCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodCategory
        fields = ['id', 'name', 'category_slug']


class CartItemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'customer', 'food_item', 'item_quantity', 'item_unit_price', 'item_total_price']
        read_only_fields = ['customer', 'item_unit_price', 'item_total_price']


class ShoppingCartSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ['id', 'customer', 'cart_items']
        read_only_fields = ['customer']


class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'customer', 'transaction_items', 'transaction_date']
        read_only_fields = ['customer', 'transaction_date']


class TransactionItemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TransactionItem
        fields = ['id', 'customer', 'food_item', 'item_quantity', 'item_unit_price', 'item_total_price']
        read_only_fields = ['customer', 'item_unit_price', 'item_total_price']


class CustomerOrderSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CustomerOrder
        fields = ['id', 'customer', 'transaction', 'assigned_delivery_person', 'is_delivered', 'order_total', 'order_date']
        read_only_fields = ['id', 'customer', 'transaction', 'assigned_delivery_person', 'order_total', 'order_date']
        extra_kwargs = {
            'assigned_delivery_person_id': {'write_only': True},
        }
