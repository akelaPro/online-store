# api/serializers/cart_serializer.py
from rest_framework import serializers
from api.models import Cart

class CartSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    items = serializers.SerializerMethodField()  # Изменили на SerializerMethodField
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'updated_at', 'items', 'total_price']
        read_only_fields = ['created_at', 'updated_at']

    def get_items(self, obj):
        from api.serializers.cart_item_serialixer import CartItemSerializer  # Ленивый импорт
        return CartItemSerializer(obj.items.all(), many=True).data

    def get_total_price(self, obj):
        return sum(item.price * item.quantity for item in obj.items.all())