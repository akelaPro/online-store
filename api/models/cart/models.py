from django.conf import settings
from django.db import models

from core import settings

class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="carts",
        verbose_name="Пользователь"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")


    def update_total_price(self):
        """Обновляет общую стоимость корзины"""
        self.total_price = sum(item.price * item.quantity for item in self.items.all())
        self.save()

    def __str__(self):
        return f"Корзина {self.user.email}"

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"