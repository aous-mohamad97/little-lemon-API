from django.contrib.auth.models import User, Group
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import get_user_model

from rest_framework.generics import (
    RetrieveAPIView,
    RetrieveUpdateAPIView,
    ListAPIView, ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    DestroyAPIView,
)
from rest_framework.response import Response
from rest_framework import status

from littlelemon.models import (
    FoodItem,
    FoodCategory,
    CartItem,
    ShoppingCart,
    CustomerOrder,
    Transaction,
    TransactionItem,
)

from .permission import (
    IsSystemAdministrator,
    IsRestaurantManager,
    IsDeliveryStaff,
    IsRegularCustomer,
    IsCustomerOrDeliveryStaff,
)

from .serializers import (
    UserGroupSerializer,
    AccountSerializer,
    FoodItemSerializer,
    FoodCategorySerializer,
    CartItemSerializer,
    ShoppingCartSerializer,
    CustomerOrderSerializer,
    TransactionSerializer,
    TransactionItemSerializer,
)

from .mixins import (
    UserFilteredDetailMixin,
    GroupManagementMixin,
    GroupMemberRemovalMixin,
    AccountHelperMixin,
    CustomerReadOnlyMixin,
    ShoppingCartHelperMixin,
    OrderProcessingMixin,
    CartItemHelperMixin,
    TransactionDetailMixin,
    ResponseHelperMixin,
)


class AccountListView(AccountHelperMixin, ListCreateAPIView):
    model = User
    queryset = model.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsRestaurantManager]
    ordering_fields = ['username', 'first_name', 'last_name']
    search_fields = ['username', 'first_name', 'last_name']
    filterset_fields = ['username', 'first_name', 'last_name']

    def check_permissions(self, request):
        self.permission_classes = [IsRestaurantManager]
        if request.method == 'POST' and self.is_unauthenticated(request):
            self.permission_classes = []
        return super().check_permissions(request)

    def get(self, request, *args, **kwargs):
        if not self.is_admin(request):
            self.queryset = self.queryset.exclude(groups__name='SysAdmin')
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        # Handle user registration with password
        data = request.data.copy()
        password = data.pop('password', None)
        
        if password:
            # Create user with password
            user = get_user_model().objects.create_user(
                username=data.get('username'),
                email=data.get('email', ''),
                password=password
            )
            # Automatically add to Customer group
            try:
                customer_group = Group.objects.get(name='Customer')
                customer_group.user_set.add(user)
            except Group.DoesNotExist:
                pass  # Group doesn't exist yet, will be created by migrations
            
            serializer = self.serializer_class(user, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Fallback to original behavior if no password provided
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class AccountDetailView(AccountHelperMixin, RetrieveUpdateDestroyAPIView):
    model = User
    queryset = model.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsCustomerOrDeliveryStaff]

    def check_permissions(self, request):
        self.permission_classes = [IsSystemAdministrator]
        if self.is_current_user(request):
            self.permission_classes = [IsCustomerOrDeliveryStaff]
        elif self.is_admin(request):
            pass
        elif self.target_is_admin(request):
            pass
        elif self.is_manager(request):
            if self.target_is_manager(request):
                if request.method in ['GET']:
                    self.permission_classes = [IsRestaurantManager]
            else:
                self.permission_classes = [IsRestaurantManager]
        return super().check_permissions(request)
    
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class UserGroupListView(ListCreateAPIView):
    model = Group
    queryset = model.objects.all()
    serializer_class = UserGroupSerializer
    permission_classes = [IsRestaurantManager]

    def get(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='SysAdmin').exists():
            self.queryset = self.queryset.exclude(name='SysAdmin')
        return super().list(request, *args, **kwargs)


class UserGroupDetailView(ModelViewSet):
    model = Group
    queryset = model.objects.all()
    serializer_class = UserGroupSerializer

    def check_permissions(self, request):
        pk = request.parser_context['kwargs']['pk']
        target_group = Group.objects.get(pk=pk)
        if request.method in ['GET']:
            if target_group.name in ['SysAdmin']:
                self.permission_classes = [IsSystemAdministrator]
            else:
                self.permission_classes = [IsRestaurantManager]
        else:
            if target_group.name not in ['SysAdmin', 'Manager']:
                self.permission_classes = [IsRestaurantManager]
            else:
                self.permission_classes = [IsSystemAdministrator]
        return super().check_permissions(request)
    
    def get(self, request, *args, **kwargs):
        group = Group.objects.get(pk=kwargs['pk'])
        serializer = self.serializer_class(group)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SystemAdminListView(GroupManagementMixin, ListAPIView):
    model = User
    queryset = model.objects.filter(groups__name='SysAdmin')
    serializer_class = AccountSerializer
    permission_classes = [IsSystemAdministrator]
    target_group = 'SysAdmin'
    ordering_fields = ['username', 'first_name', 'last_name']
    search_fields = ['username', 'first_name', 'last_name']
    filterset_fields = ['username', 'first_name', 'last_name']


class SystemAdminDetailView(GroupMemberRemovalMixin, RetrieveUpdateAPIView):
    model = User
    queryset = model.objects.filter(groups__name='SysAdmin')
    serializer_class = AccountSerializer
    permission_classes = [IsSystemAdministrator]
    target_group = 'SysAdmin'


class ManagerListView(GroupManagementMixin, ListAPIView):
    model = User
    queryset = User.objects.filter(groups__name='Manager').exclude(groups__name='SysAdmin')
    serializer_class = AccountSerializer
    target_group = 'Manager'
    ordering_fields = ['username', 'first_name', 'last_name']
    search_fields = ['username', 'first_name', 'last_name']
    filterset_fields = ['username', 'first_name', 'last_name']

    def check_permissions(self, request):
        if request.method in ['POST', 'GET']:
            self.permission_classes = [IsRestaurantManager]
        else:
            self.permission_classes = [IsSystemAdministrator]
        return super().check_permissions(request)


class ManagerDetailView(AccountHelperMixin, GroupMemberRemovalMixin, RetrieveUpdateAPIView):
    model = User
    queryset = User.objects.filter(groups__name='Manager').exclude(groups__name='SysAdmin')
    serializer_class = AccountSerializer
    target_group = 'Manager'

    def check_permissions(self, request):
        if self.is_current_user(request):
            self.permission_classes = [IsRestaurantManager]
        elif request.method in ['GET']:
            self.permission_classes = [IsRestaurantManager]
        else:
            self.permission_classes = [IsSystemAdministrator]
        return super().check_permissions(request)


class DeliveryStaffListView(GroupManagementMixin, ListAPIView):
    model = User
    queryset = User.objects.filter(groups__name='Delivery Crew').exclude(groups__name='SysAdmin').exclude(groups__name='Manager')
    serializer_class = AccountSerializer
    permission_classes = [IsRestaurantManager]
    target_group = 'Delivery Crew'
    ordering_fields = ['username', 'first_name', 'last_name']
    search_fields = ['username', 'first_name', 'last_name']
    filterset_fields = ['username', 'first_name', 'last_name']
    

class DeliveryStaffDetailView(GroupMemberRemovalMixin, RetrieveUpdateAPIView):
    model = User
    queryset = User.objects.filter(groups__name='Delivery Crew').exclude(groups__name='SysAdmin').exclude(groups__name='Manager')
    serializer_class = AccountSerializer
    permission_classes = [IsRestaurantManager]
    target_group = 'Delivery Crew'


class CustomerListView(GroupManagementMixin, ListAPIView):
    model = User
    queryset = User.objects.filter(groups__name='Customer').exclude(groups__name='SysAdmin').exclude(groups__name='Manager')
    serializer_class = AccountSerializer
    permission_classes = [IsRestaurantManager]
    target_group = 'Customer'
    ordering_fields = ['username', 'first_name', 'last_name']
    search_fields = ['username', 'first_name', 'last_name']
    filterset_fields = ['username', 'first_name', 'last_name']


class CustomerDetailView(GroupMemberRemovalMixin, RetrieveUpdateAPIView):
    model = User
    queryset = User.objects.filter(groups__name='Customer').exclude(groups__name='SysAdmin').exclude(groups__name='Manager')
    serializer_class = AccountSerializer
    permission_classes = [IsRestaurantManager]
    target_group = 'Customer'


class FoodCategoryListView(ModelViewSet):
    model = FoodCategory
    queryset = model.objects.all()
    serializer_class = FoodCategorySerializer
    ordering_fields = ['name', 'category_slug']
    search_fields = ['name', 'category_slug']
    filterset_fields = ['name', 'category_slug']

    def check_permissions(self, request):
        if request.method in ['GET']:
            self.permission_classes = [IsCustomerOrDeliveryStaff]
        else:
            self.permission_classes = [IsRestaurantManager]
        return super().check_permissions(request)


class FoodCategoryDetailView(ModelViewSet):
    model = FoodCategory
    queryset = model.objects.all()
    serializer_class = FoodCategorySerializer

    def check_permissions(self, request):
        if request.method in ['GET']:
            self.permission_classes = [IsCustomerOrDeliveryStaff]
        else:
            self.permission_classes = [IsRestaurantManager]
        return super().check_permissions(request)


class CategoryFoodItemsView(ListAPIView):
    model = FoodItem
    queryset = model.objects.all()
    serializer_class = FoodItemSerializer
    ordering_fields = ['name', 'cost', 'is_featured']
    search_fields = ['name', 'cost', 'is_featured']
    filterset_fields = ['name', 'cost', 'is_featured']

    def check_permissions(self, request):
        if request.method in ['GET']:
            self.permission_classes = [IsCustomerOrDeliveryStaff]
        else:
            self.permission_classes = [IsRestaurantManager]
        return super().check_permissions(request)
    
    def get(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(food_category__pk=kwargs['pk'])
        return super().get(request, *args, **kwargs)
    

class FoodItemListView(ModelViewSet):
    model = FoodItem
    queryset = model.objects.all()
    serializer_class = FoodItemSerializer
    ordering_fields = ['name', 'cost', 'is_featured']
    search_fields = ['name', 'cost', 'is_featured']
    filterset_fields = ['name', 'cost', 'is_featured']

    def check_permissions(self, request):
        if request.method in ['GET']:
            self.permission_classes = [IsCustomerOrDeliveryStaff]
        else:
            self.permission_classes = [IsRestaurantManager]
        return super().check_permissions(request)
    
    def get_queryset(self):
        query_param_value = self.request.query_params.get('category')
        if query_param_value is not None:
            try:
                category = FoodCategory.objects.get(pk=int(query_param_value))
            except ValueError:
                category = FoodCategory.objects.get(name=query_param_value)
            self.queryset = self.queryset.filter(food_category=category)
        return super().get_queryset()


class FoodItemDetailView(ModelViewSet):
    model = FoodItem
    queryset = model.objects.all()
    serializer_class = FoodItemSerializer

    def check_permissions(self, request):
        if request.method in ['GET']:
            self.permission_classes = [IsCustomerOrDeliveryStaff]
        else:
            self.permission_classes = [IsRestaurantManager]
        return super().check_permissions(request)


class ShoppingCartView(ShoppingCartHelperMixin, APIView):
    model = ShoppingCart
    queryset = model.objects.all()
    serializer_class = ShoppingCartSerializer
    permission_classes = [IsRegularCustomer]

    def get(self, request, *args, **kwargs):
        customer = request.user
        if not customer.groups.filter(name='Customer').exists() and len(customer.groups.all()) == 1:
            return Response({'message': 'Only Customers are allowed to own a Cart'}, status=status.HTTP_400_BAD_REQUEST)
        cart = self.get_or_create_cart(customer)
        return self.serialize_and_respond(request, cart) 

    def post(self, request, *args, **kwargs):
        customer = request.user
        if not customer.groups.filter(name='Customer').exists() and len(customer.groups.all()) == 1:
            return Response({'message': 'Only Customers are allowed to own a Cart'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            cart_item = CartItem.objects.filter(customer=customer).get(pk=request.data.get('id'))
            self.add_item_to_cart(cart_item, customer)
            return Response({}, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({'message': 'object does not exist'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, *args, **kwargs):
        customer = request.user
        if not customer.groups.filter(name='Customer').exists() and len(customer.groups.all()) == 1:
            return Response({'message': 'Only Customers are allowed to own a Cart'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            cart_item_id = request.data.get('id')
            if cart_item_id is None:
                self.clear_cart(request, customer)
            else:
                cart_item = CartItem.objects.filter(customer=customer).get(pk=cart_item_id)
                customer_cart = self.get_or_create_cart(customer)
                customer_cart.cart_items.remove(cart_item)
            return Response({}, status=status.HTTP_200_OK)
        except ValueError:
            return Response({'id': 'a valid integer is required'}, status=status.HTTP_400_BAD_REQUEST)
        except CartItem.DoesNotExist:
            return Response({'message': 'object does not exist'}, status=status.HTTP_404_NOT_FOUND)


class CartItemListView(CartItemHelperMixin, ListCreateAPIView):
    model = CartItem
    queryset = model.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsRegularCustomer]
    ordering_fields = ['customer', 'food_item']
    search_fields = ['customer', 'food_item']
    filterset_fields = ['customer', 'food_item']

    def get(self, request, *args, **kwargs):
        customer = request.user
        if not customer.groups.filter(name='Manager').exists():
            self.queryset = self.queryset.filter(customer=customer)
        return super().get(request, *args, **kwargs)
    
    def post(self, request, **kwargs):
        customer = request.user
        data = self.build_cart_item_data(request, customer, **kwargs)
        if data is None:
            return Response({'message': 'object not found'}, status=status.HTTP_404_NOT_FOUND)
        self.create_cart_item_from_data(data)
        return Response(status=status.HTTP_201_CREATED)
 

class CartItemDetailView(CartItemHelperMixin, APIView):
    model = CartItem
    queryset = model.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsRegularCustomer]

    def get(self, request, *args, **kwargs):
        try:
            customer = request.user
            if not customer.groups.filter(name='Manager').exists():
                self.queryset = self.queryset.filter(customer=customer)
            cart_item = self.queryset.get(pk=kwargs['pk'])
            serializer = self.serializer_class(cart_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except self.model.DoesNotExist:
            return Response({'message': 'object not found'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, *args, **kwargs):
        try:
            customer = request.user
            if not customer.groups.filter(name='Manager').exists():
                self.queryset = self.queryset.filter(customer=customer)
            if request.data.get('quantity') is not None:
                cart_item = self.queryset.get(pk=kwargs['pk'])
                cart_item.item_quantity = int(request.data.get('quantity'))
                cart_item.item_total_price = cart_item.item_quantity * cart_item.food_item.cost
                cart_item.save()
                return self.serialize_and_respond(request, cart_item)
            raise ValueError
        except ValueError:
            return Response({'quantity': 'field requires a valid integer'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'message': 'object not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, *args, **kwargs):
        try:
            customer = request.user
            if not customer.groups.filter(name='Manager').exists():
                self.queryset = self.queryset.filter(customer=customer)
            cart_item = self.queryset.get(pk=kwargs['pk'])
            cart_item.delete()
            return Response({}, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({'message': 'object not found'})


class CustomerOrderListView(AccountHelperMixin, OrderProcessingMixin, ListCreateAPIView):
    model = CustomerOrder
    queryset = model.objects.all()
    serializer_class = CustomerOrderSerializer
    ordering_fields = ['customer', 'assigned_delivery_person', 'is_delivered', 'order_date']
    search_fields = ['customer', 'assigned_delivery_person', 'is_delivered', 'order_date']
    filterset_fields = ['customer', 'assigned_delivery_person', 'is_delivered', 'order_date']

    def check_permissions(self, request):
        if request.method in ['GET']:
            self.permission_classes = [IsCustomerOrDeliveryStaff]
        elif request.method in ['POST']:
            self.permission_classes = [IsRegularCustomer]
        else:
            self.permission_classes = [IsRestaurantManager]
        return super().check_permissions(request)

    def get(self, request, *args, **kwargs):
        if self.is_admin(request):
            pass
        elif self.is_manager(request):
            pass
        elif self.is_delivery_staff(request):
            self.queryset = self.queryset.filter(assigned_delivery_person=request.user)
        elif self.is_customer(request):
            self.queryset = self.queryset.filter(customer=request.user)
        return super().get(request, *args, **kwargs)
    
    def post(self, request):
        customer = request.user
        customer_cart = self.get_customer_cart(customer=customer)
        if customer_cart is None:
            return Response({'message': 'the customer does not have a cart'}, status=status.HTTP_404_NOT_FOUND)
        transaction_record = self.create_transaction_from_cart(customer, customer_cart)
        self.create_order_from_transaction(customer, transaction_record)
        customer_cart.cart_items.clear()
        self.clear_customer_cart_items(customer)
        customer_cart.save()
        
        return Response(status=status.HTTP_201_CREATED)


class CustomerOrderDetailView(AccountHelperMixin, ResponseHelperMixin, RetrieveUpdateDestroyAPIView):
    model = CustomerOrder
    queryset = model.objects.all()
    serializer_class = CustomerOrderSerializer

    def check_permissions(self, request):
        if request.method in ['GET']:
            self.permission_classes = [IsCustomerOrDeliveryStaff]
        elif request.method in ['PATCH']:
            self.permission_classes = [IsDeliveryStaff]
            if request.data.get('assigned_delivery_person_id'):
                self.permission_classes = [IsRestaurantManager]
        else:
            self.permission_classes = [IsRestaurantManager]
        return super().check_permissions(request)
    
    def get(self, request, *args, **kwargs):
        customer = request.user
        if customer.groups.filter(name='Manager').exists():
            pass
        elif customer.groups.filter(name='Customer').exists():
            self.queryset = self.queryset.filter(customer=customer)
        elif customer.groups.filter(name='Delivery Crew').exists():
            self.queryset = self.queryset.filter(assigned_delivery_person=customer)
        return super().get(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        order_status = request.data.get('status')
        delivery_person_id = request.data.get('assigned_delivery_person_id')
        try:
            if self.is_admin(request):
                pass
            elif self.is_manager(request):
                pass
            elif self.is_delivery_staff(request):
                self.queryset = self.queryset.filter(assigned_delivery_person=request.user)
            order = self.queryset.get(pk=kwargs['pk'])
            if order_status is not None:
                if int(order_status) < 0 or int(order_status) > 1:
                    raise ValueError
                order.is_delivered = int(order_status)
                order.save()
            if delivery_person_id is not None:
                order.assigned_delivery_person = User.objects.get(pk=delivery_person_id)
                order.save()
            return self.serialize_and_respond(request, order)
        except CustomerOrder.DoesNotExist:
            return Response({'message': 'object not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({'status': 'requires a valid integer (0 or 1)', 'id': 'requires a valid integer'}, status=status.HTTP_400_BAD_REQUEST)


class TransactionListView(ListAPIView):
    model = Transaction
    queryset = model.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsRegularCustomer]
    ordering_fields = ['customer', 'transaction_date']
    search_fields = ['customer', 'transaction_date']
    filterset_fields = ['customer', 'transaction_date']

    def get(self, request, *args, **kwargs):
        customer = request.user
        self.queryset = self.queryset.filter(customer=customer)
        return super().get(request, *args, **kwargs)


class TransactionDetailView(TransactionDetailMixin, RetrieveAPIView, DestroyAPIView):
    model = Transaction
    queryset = model.objects.all()
    serializer_class = TransactionSerializer

    def check_permissions(self, request):
        if request.method in ['GET']:
            self.permission_classes = [IsRegularCustomer]
        else:
            self.permission_classes = [IsRestaurantManager]
        return super().check_permissions(request)
    
    def get(self, request, *args, **kwargs):
        customer = request.user
        self.queryset = self.queryset.filter(customer=customer)
        return super().get(*args, **kwargs)


class TransactionItemListView(ListAPIView):
    model = TransactionItem
    queryset = model.objects.all()
    serializer_class = TransactionItemSerializer
    permission_classes = [IsRegularCustomer]
    ordering_fields = ['customer', 'food_item', 'item_total_price']
    search_fields = ['customer', 'food_item', 'item_total_price']
    filterset_fields = ['customer', 'food_item', 'item_total_price']

    def get(self, request, *args, **kwargs):
        customer = request.user
        self.queryset = self.queryset.filter(customer=customer)
        return super().get(request, *args, **kwargs)


class TransactionItemDetailView(RetrieveUpdateDestroyAPIView):
    model = TransactionItem
    queryset = model.objects.all()
    serializer_class = TransactionItemSerializer
    permission_classes = [IsRegularCustomer]

    def check_permissions(self, request):
        if request.method in ['GET']:
            self.permission_classes = [IsRegularCustomer]
        else:
            self.permission_classes = [IsRestaurantManager]
        return super().check_permissions(request)

    def get(self, request, *args, **kwargs):
        customer = request.user
        self.queryset = self.queryset.filter(customer=customer)
        return super().get(*args, **kwargs)
