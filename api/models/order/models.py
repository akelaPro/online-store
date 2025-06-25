from django.db import models

from core import settings


class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", "В обработке"),
        ("paid", "Оплачен"),
        ("shipped", "Отправлен"),
        ("delivered", "Доставлен"),
        ("cancelled", "Отменен"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Пользователь"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="Статус"
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Общая сумма")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    shipping_address = models.TextField(verbose_name="Адрес доставки")
    payment_method = models.CharField(max_length=50, verbose_name="Способ оплаты")

    def __str__(self):
        return f"Заказ #{self.id} ({self.user.username})"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created_at"]