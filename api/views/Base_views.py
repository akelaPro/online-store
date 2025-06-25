from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from api.models import Product, Cart, CartItem
from api.models.category.models import Category
from api.serializers import ProductSerializer, CartSerializer, CartItemSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response

from api.serializers.category_serializer import CategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    filterset_fields = ['categories', 'price']
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = Product.objects.filter(available=True, moderation='3')
        
        # Фильтрация по категориям
        categories = self.request.query_params.get('categories')
        if categories:
            queryset = queryset.filter(categories__id__in=categories.split(','))
        
        # Фильтрация по цене
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
            
        return queryset.distinct()

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        # Получаем или создаем корзину для пользователя
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        # Теперь используем lookup из URL
        cart_id = self.kwargs.get('cart_pk')
        return CartItem.objects.filter(cart_id=cart_id)
    
    def perform_create(self, serializer):
        cart_id = self.kwargs.get('cart_pk')
        cart = get_object_or_404(Cart, pk=cart_id, user=self.request.user)
        product = serializer.validated_data['product']
        
        # Проверяем, есть ли уже такой товар в корзине
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={
                'quantity': serializer.validated_data['quantity'],
                'price': product.price
            }
        )
        
        if not created:
            cart_item.quantity += serializer.validated_data['quantity']
            cart_item.save()
        
        serializer.instance = cart_item
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.cart.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer 
    permission_classes = [IsAuthenticatedOrReadOnly]