# api/serializers/order_serializer.py
from rest_framework import serializers
from api.models.order.models import Order


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    items = serializers.SerializerMethodField()
    status = serializers.CharField(read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'status', 'total_price', 'items',
            'created_at', 'updated_at', 'shipping_address', 
            'payment_method', 'phone_number', 'email', 'comment'
        ]
        read_only_fields = [
            'total_price', 'created_at', 'updated_at', 'status'
        ]

    def get_items(self, obj):
        from api.serializers.order_item_serializer import OrderItemSerializer
        return OrderItemSerializer(obj.items.all(), many=True).data

    def create(self, validated_data):
        
        items_data = validated_data.pop('items', [])
        order = Order.objects.create(**validated_data)
        from api.models.orderItem.models import OrderItem
        for item_data in items_data:
            product = item_data['product']
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item_data['quantity'],
                price=product.price
            )
        
        order.update_total_price()
        return order