from django.db import models
from django.utils.text import slugify
from core import settings

class Product(models.Model):
    STATUS_CHOICES = (
        ('1', 'На удалении'),
        ('2', 'На модерации'),
        ('3', 'Одобрено'),
        ('4', 'Отклонено'),
    )

    categories = models.ManyToManyField(
        'Category',
        related_name='products',
        verbose_name='Категории'
    )
    title = models.CharField(max_length=255, verbose_name='Название')
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    image = models.ImageField(upload_to='products/', verbose_name='Изображение')
    published_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                             related_name='products', verbose_name='Автор')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата удаления')
    moderation = models.CharField(max_length=1, choices=STATUS_CHOICES,
                                default='2', verbose_name='Статус модерации')
    available = models.BooleanField(default=True, verbose_name='Доступен')  # Добавлено поле

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-published_at']