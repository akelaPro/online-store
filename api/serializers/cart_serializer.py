from rest_framework import serializers
from api.models import *

class CartSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )  # Автоматически берется текущий пользователь

    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']