import secrets
from django.db import models
from api.models import *
from core import settings


class Review(models.Model):
    RATING_CHOICES = (
        (1, "1 звезда"),
        (2, "2 звезды"),
        (3, "3 звезды"),
        (4, "4 звезды"),
        (5, "5 звезд"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Пользователь"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Товар"
    )
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, verbose_name="Рейтинг")
    comment = models.TextField(verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Отзыв от {self.user.username} на {self.product.name}"

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-created_at"]