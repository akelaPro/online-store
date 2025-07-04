from django.shortcuts import render
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from api.models.order.models import Order




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


@login_required
def checkout_view(request):
    return render(request, 'frontend/checkout.html')

@login_required
def order_success_view(request, order_id):
    return render(request, 'frontend/order_success.html', {'order_id': order_id})

@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'frontend/order_detail.html', {'order': order})

@login_required
def user_orders_view(request):
    return render(request, 'frontend/user_orders.html')