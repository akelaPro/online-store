from django.urls import path, include
from rest_framework_nested import routers
from rest_framework.routers import DefaultRouter
from api.views import ProductViewSet, CartViewSet, CartItemViewSet
from api.views.Base_views import CategoryViewSet, OrderViewSet
from api.views.auth import AuthCheckView, CookieTokenObtainPairView, CookieTokenRefreshView, LogoutView, RegistrationAPIView
from api.views.chat import ChatRoomViewSet, MessageViewSet



app_name = 'api'


router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'rooms', ChatRoomViewSet, basename='chatroom')
router.register(r'messages', MessageViewSet, basename='message')
cart_router = routers.NestedSimpleRouter(router, r'cart', lookup='cart')
cart_router.register(r'items', CartItemViewSet, basename='cart-items')




urlpatterns = [
    # JWT-эндпоинты
    path('', include(router.urls)),
    path('', include(cart_router.urls)),
    path('auth/jwt/create/', CookieTokenObtainPairView.as_view(), name='jwt-create'),  # Логин (получение токена)
    path('auth/jwt/refresh/', CookieTokenRefreshView.as_view(), name='jwt-refresh'),   # Обновление токена
   
    
    path('auth/register/', RegistrationAPIView.as_view(), name='register'),             # Регистрация
    path('auth/logout/', LogoutView.as_view(), name='logout'),                   # Выход
    path('check_auth/', AuthCheckView.as_view(), name='check_auth'),              # Проверка аутентификации
]

