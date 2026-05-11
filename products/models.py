from django.db import models
from cloudinary.models import CloudinaryField

class Category(models.Model):
    name = models.CharField(max_length=20, unique=True)
    slug = models.SlugField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    category = models.ForeignKey(Category, related_name='items', on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_available = models.BooleanField(default=True, db_index=True)
    stock_quantity = models.PositiveIntegerField(default=25)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    image = CloudinaryField('image', blank=True, null=True)  # <-- Updated field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def stock_status(self):
        if self.stock_quantity <= 0 or not self.is_available:
            return "out"
        if self.stock_quantity <= self.low_stock_threshold:
            return "low"
        return "in_stock"
