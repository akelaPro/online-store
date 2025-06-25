from rest_framework import serializers
from api.models import *
from api.models.review.models import Review
from api.serializers.product_serializer import ProductSerializer


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True,
        label="ID товара"
    )

    class Meta:
        model = Review
        fields = ['id', 'user', 'product', 'product_id', 'rating', 'comment', 'created_at']
        read_only_fields = ['created_at']

    def validate_rating(self, value):
        if value not in range(1, 6):
            raise serializers.ValidationError("Рейтинг должен быть от 1 до 5")
        return value