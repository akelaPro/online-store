from django.contrib import admin
from django.urls import include, path
from frontend.views import *


app_name = 'frontend'
urlpatterns = [
    path('', home, name='home'),
    path('cart/', cart, name='cart'),
]