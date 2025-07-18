from django.urls import include, path
from frontend.views import *


app_name = 'frontend'
urlpatterns = [
    path('', home, name='home'),
    path('cart/', CartTemplateView.as_view(), name='cart'),
    path('product/<int:pk>/', productTemplateView.as_view(), name='photo_detail'),
    path('login/', LoginTemplateView.as_view(), name='login'),
    path('register/', RegistrationTemplateView.as_view(), name='register'),
    path('checkout/', checkout_view, name='checkout'),
    path('order-success/<int:order_id>/', order_success_view, name='order_success'),
    path('orders/<int:order_id>/', order_detail_view, name='order_detail'),
    path('my-orders/', user_orders_view, name='user_orders'),
    path('chat/', chat_view, name='chat'),
    path('admin-chats/', admin_chat_list, name='admin_chat_list'),
    path('admin-chats/<int:room_id>/', admin_chat_detail, name='admin_chat_detail'),
    
]