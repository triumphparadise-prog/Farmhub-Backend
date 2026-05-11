import bleach
from rest_framework import serializers
from .models import MenuItem, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class SafeImageField(serializers.ImageField):
    def to_representation(self, value):
        if not value:
            return None

        try:
            return super().to_representation(value)
        except Exception:
            fallback = str(value).strip()
            return fallback or None


class MenuItemSerializer(serializers.ModelSerializer):
    image = SafeImageField(required=False, allow_null=True)
    category_detail = CategorySerializer(source="category", read_only=True)
    category_label = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = MenuItem
        fields = '__all__'

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Name too short.")
        return bleach.clean(value, tags=[], strip=True)

    def validate_description(self, value):
        value = value.strip()
        return bleach.clean(value, tags=[], strip=True)

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0.")
        return value
