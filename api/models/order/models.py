from django.db import models
from django.core.validators import MinValueValidator
from core import settings
from django.core.validators import RegexValidator




phone_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Номер телефона должен быть в формате: '+999999999'. Допускается до 15 цифр."
    )


class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", "В обработке"),
        ("paid", "Оплачен"),
        ("shipped", "Отправлен"),
        ("delivered", "Доставлен"),
        ("cancelled", "Отменен"),
    )

    PAYMENT_METHOD_CHOICES = (
        ("cash", "Наличные при получении"),
        ("card", "Онлайн оплата картой"),
        ("sbp", "СБП (Система быстрых платежей)"),
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
    total_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Общая сумма",
        validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    shipping_address = models.TextField(verbose_name="Адрес доставки")
    payment_method = models.CharField(
        max_length=50, 
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name="Способ оплаты"
    )
    phone_number = models.CharField(
    max_length=20,
    verbose_name="Номер телефона",
    default="",  # пустая строка как временное значение
    blank=False  # обязательно для новых записей
)
    email = models.EmailField(
    verbose_name="Email",
    default="user@example.com"  
)
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий к заказу")

    def __str__(self):
        return f"Заказ #{self.id} ({self.user.username})"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created_at"]

    def update_total_price(self):
        self.total_price = sum(item.price * item.quantity for item in self.items.all())
        self.save()


    