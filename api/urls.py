from django.urls import path

from .views import (
    AccountDetailView, AccountListView,
    UserGroupListView, UserGroupDetailView,
    SystemAdminListView, SystemAdminDetailView,
    ManagerListView, ManagerDetailView,
    DeliveryStaffListView, DeliveryStaffDetailView,
    CustomerListView, CustomerDetailView,
    FoodItemListView, FoodItemDetailView,
    FoodCategoryListView, FoodCategoryDetailView, CategoryFoodItemsView,
    CartItemListView, CartItemDetailView,
    ShoppingCartView,
    CustomerOrderListView, CustomerOrderDetailView,
    TransactionListView, TransactionDetailView,
    TransactionItemListView, TransactionItemDetailView,
)

LIST = {'get': 'list', 'post': 'create'}
DETAIL = {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}


urlpatterns = [
    path('users', AccountListView.as_view()),
    path('users/<int:pk>', AccountDetailView.as_view(), name='account-detail'),

    path('groups', UserGroupListView.as_view()),
    path('groups/<int:pk>', UserGroupDetailView.as_view(DETAIL)),
    path('groups/admins', SystemAdminListView.as_view()),
    path('groups/admins/<int:pk>', SystemAdminDetailView.as_view()),
    path('groups/managers', ManagerListView.as_view()),
    path('groups/managers/<int:pk>', ManagerDetailView.as_view()),
    path('groups/delivery-crew', DeliveryStaffListView.as_view()),
    path('groups/delivery-crew/<int:pk>', DeliveryStaffDetailView.as_view()),
    path('groups/customers', CustomerListView.as_view()),
    path('groups/customers/<int:pk>', CustomerDetailView.as_view()),

    path('menu-items', FoodItemListView.as_view(LIST)),
    path('menu-items/<int:pk>', FoodItemDetailView.as_view(DETAIL), name='fooditem-detail'),
    path('categories', FoodCategoryListView.as_view(LIST)),
    path('categories/<int:pk>', FoodCategoryDetailView.as_view(DETAIL), name='category-detail'),
    path('categories/<int:pk>/menu-items', CategoryFoodItemsView.as_view()),
    path('order-items', CartItemListView.as_view()),
    path('order-items/<int:pk>', CartItemDetailView.as_view(), name='cartitem-detail'),

    path('cart', ShoppingCartView.as_view()),

    path('orders', CustomerOrderListView.as_view()),
    path('orders/<int:pk>', CustomerOrderDetailView.as_view(), name='order-detail'),

    path('purchases', TransactionListView.as_view()),
    path('purchases/<int:pk>', TransactionDetailView.as_view(), name='transaction-detail'),

    path('purchase-items', TransactionItemListView.as_view()),
    path('purchase-items/<int:pk>', TransactionItemDetailView.as_view(), name='transactionitem-detail'),
]