# api/serializers/order_item_serializer.py
from rest_framework import serializers
from api.models import Product, OrderItem
from api.serializers.product_serializer import ProductSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True,
        label="ID товара"
    )
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'id', 'order', 'product', 'product_id', 
            'quantity', 'price', 'total_price'
        ]
        read_only_fields = ['order', 'price', 'total_price']

    def get_total_price(self, obj):
        return obj.price * obj.quantity