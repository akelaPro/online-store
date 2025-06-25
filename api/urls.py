from django.urls import path, include
from rest_framework_nested import routers
from rest_framework.routers import DefaultRouter
from api.views import ProductViewSet, CartViewSet, CartItemViewSet
from api.views.Base_views import CategoryViewSet
from api.views.auth import CheckAuthView, LogoutView, RegisterView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
) 



app_name = 'api'


router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'cart', CartViewSet, basename='cart')

cart_router = routers.NestedSimpleRouter(router, r'cart', lookup='cart')
cart_router.register(r'items', CartItemViewSet, basename='cart-items')




urlpatterns = [
    # JWT-эндпоинты
    path('', include(router.urls)),
    path('', include(cart_router.urls)),
    path('auth/jwt/create/', TokenObtainPairView.as_view(), name='jwt-create'),  # Логин (получение токена)
    path('auth/jwt/refresh/', TokenRefreshView.as_view(), name='jwt-refresh'),   # Обновление токена
    path('auth/jwt/verify/', TokenVerifyView.as_view(), name='jwt-verify'),      # Проверка токена
    
    # Кастомные эндпоинты
    path('auth/register/', RegisterView.as_view(), name='register'),             # Регистрация
    path('auth/logout/', LogoutView.as_view(), name='logout'),                   # Выход
    path('check_auth/', CheckAuthView.as_view(), name='check_auth'),              # Проверка аутентификации
]

