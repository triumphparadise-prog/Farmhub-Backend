# orders/models.py
from django.db import models
from django.contrib.auth import get_user_model
from products.models import MenuItem
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('OUT_FOR_DELIVERY', 'Out for delivery'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', db_index=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estimated_delivery_date = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    paystack_reference = models.CharField(max_length=255, blank=True, null=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Order #{self.id} - {self.user}"

    def ensure_delivery_estimate(self):
        if not self.estimated_delivery_date:
            self.estimated_delivery_date = timezone.localdate() + timedelta(days=2)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def line_total(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name if self.menu_item else 'Deleted Item'}"
