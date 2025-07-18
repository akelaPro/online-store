from django.shortcuts import redirect, render
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from api.models.chat.models import ChatRoom, Message
from api.models.order.models import Order
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model


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

@login_required
def chat_view(request):
    try:
        room = ChatRoom.get_or_create_for_user(request.user)  # Вызываем через класс
        messages = Message.objects.filter(room=room).order_by('timestamp')[:50]
        return render(request, 'frontend/chat.html', {
            'room': room,
            'request': request,
            'messages': messages
        })
    except Exception as e:
        print(f"Error in chat_view: {e}")
        messages.error(request, f"Ошибка чата: {e}")
        return render(request, 'frontend/chat.html', {
            'error': str(e),
            'request': request
        })
    



User = get_user_model()

def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin)
def admin_chat_list(request):
    chats = ChatRoom.objects.all().order_by('-created_at')
    return render(request, 'frontend/admin/admin_chat_list.html', {'chats': chats})

@user_passes_test(is_admin)
def admin_chat_detail(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    messages = room.messages.all().order_by('timestamp')
    
    # Помечаем сообщения как прочитанные
    room.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    
    return render(request, 'frontend/admin/admin_chat_detail.html', {
        'room': room,
        'messages': messages,
    })

