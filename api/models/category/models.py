from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=150, db_index=True, verbose_name='Название категории')  
    slug = models.SlugField(max_length=150, unique=True) 
    


    def __str__(self):
        return self.name

    class Meta:
        db_table = ''
        managed = True
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'