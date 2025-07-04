from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from api.models import Product, Cart, CartItem
from api.models.category.models import Category
from api.models.order.models import Order
from api.models.orderItem.models import OrderItem
from api.serializers import ProductSerializer, CartSerializer, CartItemSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from api.serializers.category_serializer import CategorySerializer
from api.serializers.order_serializer import OrderSerializer
from rest_framework.decorators import action





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




class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')

    @action(detail=False, methods=['post'], url_path='create-from-cart')
    def create_from_cart(self, request):
        """
        Создает заказ из текущей корзины пользователя
        """
        cart = Cart.objects.get_or_create(user=request.user)[0]
        cart_items = CartItem.objects.filter(cart=cart).select_related('product')
        
        if not cart_items.exists():
            return Response(
                {"detail": "Корзина пуста"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Создаем заказ
        order = Order.objects.create(
            user=request.user,
            shipping_address=request.data.get('shipping_address'),
            payment_method=request.data.get('payment_method'),
            phone_number=request.data.get('phone_number'),
            email=request.data.get('email', request.user.email),
            comment=request.data.get('comment', ''),
            status='created'
        )

        # Добавляем товары в заказ
        order_items = []
        for item in cart_items:
            order_items.append(OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.price
            ))
        
        OrderItem.objects.bulk_create(order_items)
        
        # Очищаем корзину
        cart_items.delete()
        cart.update_total_price()

        # Сериализуем и возвращаем ответ
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)