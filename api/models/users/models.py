import secrets
from django.db import models
from django.contrib.auth.models import AbstractUser  
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models




class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        
        email = self.normalize_email(email)
        # Генерируем username если не указан
        if 'username' not in extra_fields:
            extra_fields['username'] = email.split('@')[0]
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser ):
    username = models.CharField(max_length=150, blank=True, null=True)
    first_name = models.CharField(max_length=150, verbose_name='Имя', blank=True, null=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, default='avatars/default_avatar.png')
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    avatar_thumbnail = ImageSpecField(
        source='avatar',
        processors=[ResizeToFill(100, 100)], 
        format='PNG',
        options={'quality': 60}
    )


    USERNAME_FIELD = 'email'  # Используем email для входа
    REQUIRED_FIELDS = []


    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


