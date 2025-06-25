from rest_framework import serializers

from api.models.cart_item.models import CartItem
from api.models.product.models import Product
from api.serializers.cart_serializer import CartSerializer
from api.serializers.product_serializer import ProductSerializer



class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'price']
        read_only_fields = ['id', 'product', 'price']

    def create(self, validated_data):
        # Этот метод будет вызываться автоматически при сохранении
        product = validated_data['product']
        validated_data['price'] = product.price
        return super().create(validated_data)