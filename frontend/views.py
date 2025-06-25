from django.shortcuts import render
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.views.generic import TemplateView


def home(request):
    return render(request, 'frontend/index.html')

def cart(request):
    return render(request, 'frontend/cart.html')