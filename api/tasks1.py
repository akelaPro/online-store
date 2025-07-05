from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Order

@shared_task(bind=True, max_retries=3)
def send_order_confirmation_email(self, order_id):
    try:
        order = Order.objects.get(id=order_id)
        
        subject = f"Ваш заказ #{order.id} принят"
        html_message = render_to_string('frontend/emails/order_confirmation.html', {
            'order': order,
            'items': order.items.all()
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject,
            plain_message,
            None,  # Используется DEFAULT_FROM_EMAIL
            [order.email],
            html_message=html_message,
            fail_silently=False
        )
        
        return f"Email sent for order {order_id}"
    except Exception as e:
        self.retry(exc=e, countdown=60)  # Повтор через 60 сек