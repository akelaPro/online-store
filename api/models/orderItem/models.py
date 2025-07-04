from django.db import models
from api.models.order.models import Order
from api.models.product.models import Product
from django.core.validators import MinValueValidator


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Заказ"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        related_name="order_items",
        verbose_name="Товар"
    )
    quantity = models.PositiveIntegerField(
        verbose_name="Количество",
        validators=[MinValueValidator(1)]
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Цена за единицу",
        validators=[MinValueValidator(0)]
    )

    def __str__(self):
        return f"{self.product.name if self.product else 'Товар удален'} ({self.quantity})"

    class Meta:
        verbose_name = "Элемент заказа"
        verbose_name_plural = "Элементы заказа"

    @property
    def total_price(self):
        return self.price * self.quantity