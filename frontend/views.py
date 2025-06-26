from django.shortcuts import render
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.views.generic import TemplateView


def home(request):
    return render(request, 'frontend/index.html')


class RegistrationTemplateView(TemplateView):
    template_name = 'frontend/register.html'


class LoginTemplateView(TemplateView):
    template_name = 'frontend/login.html'

class CartTemplateView(TemplateView):
    template_name = 'frontend/cart.html'

class productTemplateView(TemplateView):
    template_name = 'frontend/product_detail.html'