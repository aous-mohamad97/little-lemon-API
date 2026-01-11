from django.db import models
from django.contrib.auth.models import User


class FoodItem(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    cost = models.DecimalField(max_digits=6, decimal_places=2)
    is_featured = models.BooleanField(default=False)
    food_category = models.ForeignKey('littlelemon.FoodCategory', on_delete=models.PROTECT, related_name='items')

    class Meta:
        ordering = ['name']
        verbose_name = 'Food Item'
        verbose_name_plural = 'Food Items'

    def __str__(self):
        return self.name


class FoodCategory(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    category_slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Food Category'
        verbose_name_plural = 'Food Categories'

    def __str__(self):
        return self.name


class CartItem(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    food_item = models.ForeignKey(FoodItem, on_delete=models.PROTECT, related_name='cart_items')
    item_quantity = models.SmallIntegerField(default=1)
    item_unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    item_total_price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ['customer', 'food_item']
        ordering = ['-id']
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'

    def __str__(self):
        return f'{self.customer.username} - {self.food_item.name} (x{self.item_quantity})'


class ShoppingCart(models.Model):
    customer = models.OneToOneField(User, on_delete=models.CASCADE, related_name='shopping_cart')
    cart_items = models.ManyToManyField(CartItem, related_name='carts', blank=True)

    class Meta:
        verbose_name = 'Shopping Cart'
        verbose_name_plural = 'Shopping Carts'

    def __str__(self):
        return f'Shopping cart for {self.customer.username}'

    def get_total(self):
        return sum(item.item_total_price for item in self.cart_items.all())


class TransactionItem(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transaction_items')
    food_item = models.ForeignKey(FoodItem, on_delete=models.PROTECT, related_name='transaction_items')
    item_quantity = models.SmallIntegerField()
    item_unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    item_total_price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        ordering = ['-id']
        verbose_name = 'Transaction Item'
        verbose_name_plural = 'Transaction Items'

    def __str__(self):
        return f'Transaction item: {self.food_item.name} for {self.customer.username}'


class Transaction(models.Model):
    customer = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=0, related_name='transactions')
    transaction_items = models.ManyToManyField(TransactionItem, related_name='transactions', blank=True)
    transaction_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-transaction_date']
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'

    def __str__(self):
        return f'Transaction #{self.id} - {self.customer.username} on {self.transaction_date.strftime("%Y-%m-%d")}'

    def get_total(self):
        return sum(item.item_total_price for item in self.transaction_items.all())


class CustomerOrder(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_orders')
    transaction = models.OneToOneField(Transaction, on_delete=models.PROTECT, related_name='order')
    assigned_delivery_person = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_orders',
        null=True,
        blank=True,
    )
    is_delivered = models.BooleanField(db_index=True, default=False)
    order_total = models.DecimalField(max_digits=6, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-order_date']
        verbose_name = 'Customer Order'
        verbose_name_plural = 'Customer Orders'

    def __str__(self):
        status = 'Delivered' if self.is_delivered else 'Pending'
        return f'Order #{self.id} - {self.customer.username} ({status})'
