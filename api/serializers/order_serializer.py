from rest_framework import serializers
from api.models import *

class OrderSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    status = serializers.CharField(read_only=True)  # Статус меняется через админку/логику

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'status', 'total_price',
            'created_at', 'updated_at', 'shipping_address', 'payment_method'
        ]
        read_only_fields = ['total_price', 'created_at', 'updated_at']