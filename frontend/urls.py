from django.contrib import admin
from django.urls import include, path
from frontend.views import *


app_name = 'frontend'
urlpatterns = [
    path('', home, name='home'),
    path('cart/', CartTemplateView.as_view(), name='cart'),
    path('product/<int:pk>/', productTemplateView.as_view(), name='photo_detail'),
    path('login/', LoginTemplateView.as_view(), name='login'),
    path('register/', RegistrationTemplateView.as_view(), name='register'),


    
]