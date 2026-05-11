from decimal import Decimal
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import serializers
from .models import Order, OrderItem
from products.models import MenuItem
from products.serializers import MenuItemSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_detail = MenuItemSerializer(source='menu_item', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'menu_item_detail', 'quantity', 'price']
        read_only_fields = ['id', 'menu_item_detail', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    customer = serializers.ReadOnlyField(source='user.username')
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'status', 'total_price', 'delivery_fee',
            'estimated_delivery_date', 'address', 'phone',
            'created_at', 'items', 'paid', 'paystack_reference'
        ]
        read_only_fields = [
            'id', 'total_price', 'delivery_fee', 'estimated_delivery_date',
            'created_at', 'paid', 'paystack_reference'
        ]

    # FIELD VALIDATION
    def validate_address(self, value):
        if value is None:
            return value
        value = value.strip()
        if len(value) < 5:  # Stronger validation
            raise serializers.ValidationError("Address is too short (minimum 5 characters).")
        return value

    def validate_phone(self, value):
        if value is None:
            return value
        value = value.strip()
        if not value.isdigit() or len(value) < 8:
            raise serializers.ValidationError("Invalid phone number.")
        return value

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Order must contain at least one item.")
        return value

    def _delivery_fee_for_address(self, address):
        text = (address or "").lower()
        if any(area in text for area in ["lagos island", "lekki", "ajah", "vi"]):
            return Decimal("2500.00")
        if any(area in text for area in ["ibadan", "abeokuta", "ogun", "oyo"]):
            return Decimal("3500.00")
        return Decimal("1500.00")

    def _send_order_receipt(self, order):
        user = order.user
        if not user or not getattr(user, "email", None):
            return

        lines = [
            f"Order #{order.id} received.",
            "",
            "Items:",
        ]
        for item in order.items.select_related("menu_item"):
            name = item.menu_item.name if item.menu_item else "Deleted item"
            lines.append(f"- {item.quantity} x {name}: NGN {item.price * item.quantity}")
        lines.extend(
            [
                "",
                f"Delivery fee: NGN {order.delivery_fee}",
                f"Total: NGN {order.total_price}",
                f"Estimated delivery: {order.estimated_delivery_date}",
                "",
                "Thank you for shopping with FarmHub.",
            ]
        )

        try:
            send_mail(
                subject=f"FarmHub Order #{order.id} Receipt",
                message="\n".join(lines),
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception:
            return

    # CREATE ORDER
    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        
        # Safe context retrieval
        request = self.context.get('request')
        user = request.user if request and hasattr(request, 'user') else None

        order = Order.objects.create(user=user, **validated_data)
        total = Decimal('0.00')

        for item in items_data:
            # Flexible menu item lookup
            menu_item_obj = None
            if isinstance(item.get('menu_item'), int):
                menu_item_obj = MenuItem.objects.get(id=item.get('menu_item'))
            elif isinstance(item.get('menu_id'), int):
                menu_item_obj = MenuItem.objects.get(id=item.get('menu_id'))
            elif isinstance(item.get('menu_item'), MenuItem):
                menu_item_obj = item.get('menu_item')
            else:
                raise serializers.ValidationError("Invalid menu_item entry.")

            if not menu_item_obj.is_available or menu_item_obj.stock_quantity <= 0:
                raise serializers.ValidationError(f"Item '{menu_item_obj.name}' is not available.")

            quantity = int(item.get('quantity', 1))
            if quantity <= 0:
                raise serializers.ValidationError(f"Invalid quantity for '{menu_item_obj.name}'.")
            if quantity > menu_item_obj.stock_quantity:
                raise serializers.ValidationError(
                    f"Only {menu_item_obj.stock_quantity} unit(s) of '{menu_item_obj.name}' are available."
                )

            price = Decimal(menu_item_obj.price)

            OrderItem.objects.create(
                order=order,
                menu_item=menu_item_obj,
                quantity=quantity,
                price=price
            )

            total += price * quantity
            menu_item_obj.stock_quantity -= quantity
            if menu_item_obj.stock_quantity <= 0:
                menu_item_obj.is_available = False
            menu_item_obj.save(update_fields=["stock_quantity", "is_available", "updated_at"])

        order.delivery_fee = self._delivery_fee_for_address(order.address)
        order.ensure_delivery_estimate()
        total += order.delivery_fee
        order.total_price = total
        order.save()
        self._send_order_receipt(order)
        return order

    # UPDATE ORDER
    def update(self, instance, validated_data):
        validated_data.pop('items', None)
        return super().update(instance, validated_data)
