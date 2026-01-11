from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth.models import User, Group

from .permission import (
    IsSystemAdministrator,
    IsRestaurantManager,
    IsDeliveryStaff,
    IsRegularCustomer,
)

from littlelemon.models import (
    FoodCategory,
    FoodItem,
    CartItem,
    ShoppingCart,
    CustomerOrder,
    TransactionItem,
    Transaction,
)


class AccountHelperMixin:
    def is_current_user(self, request):
        current_user_id = request.user.pk
        target_user_id = request.parser_context['kwargs'].get('pk')
        return current_user_id == target_user_id and target_user_id is not None

    def belongs_to_group(self, request, group_name=''):
        return request.user.groups.filter(name=group_name).exists()

    def target_user_belongs_to_group(self, request, group_name=''):
        target_user_id = request.parser_context['kwargs'].get('pk')
        try:
            target_user = User.objects.get(pk=target_user_id)
            return target_user.groups.filter(name=group_name).exists()
        except User.DoesNotExist:
            return False
    
    def is_unauthenticated(self, request):
        return request.user.is_anonymous

    def is_customer(self, request):
        return self.belongs_to_group(request, group_name='Customer')

    def is_delivery_staff(self, request):
        return self.belongs_to_group(request, group_name='Delivery Crew')

    def is_manager(self, request):
        return self.belongs_to_group(request, group_name='Manager')

    def is_admin(self, request):
        return self.belongs_to_group(request, group_name='SysAdmin')

    def target_is_customer(self, request):
        return self.target_user_belongs_to_group(request, group_name='Customer')

    def target_is_delivery_staff(self, request):
        return self.target_user_belongs_to_group(request, group_name='Delivery Crew')

    def target_is_manager(self, request):
        return self.target_user_belongs_to_group(request, group_name='Manager')

    def target_is_admin(self, request):
        return self.target_user_belongs_to_group(request, group_name='SysAdmin')


class ResponseHelperMixin:
    def serialize_and_respond(self, request, obj, response_status=status.HTTP_200_OK):
        serializer = self.serializer_class(obj, context={'request': request})
        return Response(serializer.data, status=response_status)

    def get_target_customer(self, **kwargs):
        customer_queryset = User.objects.filter(groups__name='Customer').exclude(groups__name='Manager')
        try:
            return customer_queryset.get(pk=kwargs['pk'])
        except User.DoesNotExist:
            return None


class UserFilteredListMixin(ListCreateAPIView):
    related_model = None

    def get(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(customer=request.user)
        return super().get(request, *args, **kwargs)
    

class UserFilteredDetailMixin(RetrieveUpdateDestroyAPIView):
    def get(self, request, *args, **kwargs):
        try:
            self.queryset = self.queryset.filter(customer=request.user)
            return super().retrieve(request, *args, **kwargs)
        except self.model.DoesNotExist:
            return Response({'message': 'object not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def patch(self, request, *args, **kwargs):
        try:
            self.queryset = self.queryset.filter(customer=request.user)
            return super().partial_update(request, *args, **kwargs)
        except self.model.DoesNotExist:
            return Response({'message': 'object not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, *args, **kwargs):
        try:
            self.queryset = self.queryset.filter(customer=request.user)
            return super().destroy(request, *args, **kwargs)
        except self.model.DoesNotExist:
            return Response({'message': 'object not found'}, status=status.HTTP_404_NOT_FOUND)


class GroupManagementMixin:
    target_group = ''

    def post(self, request):
        try:
            user_id = int(request.data.get('id'))
            target_user = User.objects.get(pk=user_id)
            target_group = Group.objects.get(name=self.target_group)
            target_group.user_set.add(target_user)
            target_group.save()
            return Response(self.serializer_class(target_user).data, status=status.HTTP_201_CREATED)
        except ValueError:
            return Response({'id': 'a valid integer is required'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'message': 'object not found'}, status=status.HTTP_404_NOT_FOUND)
        

class GroupMemberRemovalMixin:
    def delete(self, request, *args, **kwargs):
        try:
            target_user = User.objects.get(pk=kwargs['pk'])
            target_group = Group.objects.get(name=self.target_group)
            target_group.user_set.remove(target_user)
            target_group.save()
            return Response({'message': 'user removed from the group'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'object not found'}, status=status.HTTP_404_NOT_FOUND)


class CustomerReadOnlyMixin:
    def check_permissions(self, request):
        if request.method not in ['GET']:
            self.permission_classes = [IsRestaurantManager]
        else:
            self.permission_classes = [IsRegularCustomer]
        return super().check_permissions(request)


class ShoppingCartHelperMixin(ResponseHelperMixin):
    def get_or_create_cart(self, customer):
        try:
            return self.model.objects.get(customer=customer)
        except self.model.DoesNotExist:
            cart = self.model.objects.create(customer=customer)
            cart.save()
            return cart

    def create_cart_item(self, request, customer, food_item_obj):
        quantity = request.data.get('quantity', 1)
        quantity = 1 if quantity is None else int(quantity)
        unit_price = food_item_obj.cost
        total_price = unit_price * quantity

        cart_item = CartItem.objects.create(
            customer=customer,
            food_item=food_item_obj,
            item_quantity=quantity,
            item_unit_price=unit_price,
            item_total_price=total_price, 
        )
        return cart_item

    def get_cart_item(self, request, customer):
        try:
            item_id = int(request.data.get('id'))
            cart_item = CartItem.objects.filter(customer=customer).get(pk=item_id)
            return cart_item
        except CartItem.DoesNotExist:
            return None

    def add_item_to_cart(self, cart_item_obj, customer):
        cart = self.get_or_create_cart(customer)
        cart.cart_items.add(cart_item_obj)
        cart.save()
    
    def remove_item_from_cart(self, cart_item_obj, customer):
        cart = self.get_or_create_cart(customer)
        cart.cart_items.remove(cart_item_obj)
        cart.save()
    
    def clear_cart(self, request, customer):
        cart = self.get_or_create_cart(customer)
        cart.cart_items.clear()
        cart.save()


class CartItemHelperMixin(ResponseHelperMixin):
    def build_cart_item_data(self, request, customer, **kwargs):
        try:
            food_item_obj = FoodItem.objects.get(pk=request.data.get('id'))
            quantity = request.data.get('quantity', 1)
            quantity = 1 if quantity is None else int(quantity)
            unit_price = food_item_obj.cost
            total_price = unit_price * quantity

            return {
                'customer': customer,
                'food_item': food_item_obj,
                'quantity': quantity,
                'unit_price': unit_price,
                'total_price': total_price,
            }
        except FoodItem.DoesNotExist:
            return None

    def create_cart_item_from_data(self, data):
        cart_item = CartItem.objects.create(
            customer=data['customer'],
            food_item=data['food_item'],
            item_quantity=data['quantity'],
            item_unit_price=data['unit_price'],
            item_total_price=data['total_price'],
        )
        return cart_item


class OrderProcessingMixin(ResponseHelperMixin):
    def get_customer_cart(self, customer):
        try:
            return ShoppingCart.objects.get(customer=customer)
        except ShoppingCart.DoesNotExist:
            return None
    
    def create_transaction_item_from_cart_item(self, cart_item):
        transaction_item = TransactionItem.objects.create(
            customer=cart_item.customer,
            food_item=cart_item.food_item,
            item_quantity=cart_item.item_quantity,
            item_unit_price=cart_item.item_unit_price,
            item_total_price=cart_item.item_total_price,
        )
        transaction_item.save()
        return transaction_item
    
    def create_transaction_from_cart(self, customer, customer_cart):
        transaction = Transaction.objects.create(customer=customer)
        for cart_item in customer_cart.cart_items.all():
            transaction_item = self.create_transaction_item_from_cart_item(cart_item)
            transaction.transaction_items.add(transaction_item)
        transaction.save()
        return transaction
    
    def calculate_transaction_total(self, transaction_record):
        return sum(item.item_total_price for item in transaction_record.transaction_items.all())
    
    def create_order_from_transaction(self, customer, transaction_record):
        order = self.model.objects.create(
            customer=customer,
            transaction=transaction_record,
            order_total=self.calculate_transaction_total(transaction_record)
        )
        order.save()
        return order
    
    def clear_customer_cart_items(self, customer):
        CartItem.objects.filter(customer=customer).delete()
        return not CartItem.objects.filter(customer=customer).exists()


class TransactionDetailMixin(ResponseHelperMixin):
    pass
