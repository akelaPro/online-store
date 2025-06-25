from rest_framework import serializers
from api.models import Product, Category
from api.serializers.category_serializer import CategorySerializer

class ProductSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)  # Для ManyToMany используем many=True
    categories_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Category.objects.all(),
        source='categories',
        write_only=True,
        label="ID категорий"
    )

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'description', 'price',
            'categories', 'categories_ids', 'image',
            'published_at', 'author', 'moderation', 'available'
        ]
        read_only_fields = ['slug', 'published_at', 'author']