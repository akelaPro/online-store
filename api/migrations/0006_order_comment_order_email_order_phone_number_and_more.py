# Generated by Django 5.2.3 on 2025-07-04 15:02

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_alter_user_managers'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='comment',
            field=models.TextField(blank=True, null=True, verbose_name='Комментарий к заказу'),
        ),
        migrations.AddField(
            model_name='order',
            name='email',
            field=models.EmailField(default='user@example.com', max_length=254, verbose_name='Email'),
        ),
        migrations.AddField(
            model_name='order',
            name='phone_number',
            field=models.CharField(default='', max_length=20, verbose_name='Номер телефона'),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('cash', 'Наличные при получении'), ('card', 'Онлайн оплата картой'), ('sbp', 'СБП (Система быстрых платежей)')], max_length=50, verbose_name='Способ оплаты'),
        ),
        migrations.AlterField(
            model_name='order',
            name='total_price',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Общая сумма'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Цена за единицу'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='quantity',
            field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Количество'),
        ),
    ]
