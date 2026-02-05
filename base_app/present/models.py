from django.db import models


class Product(models.Model):

    title = models.CharField(
        max_length=200,
        help_text="Название товара",
        verbose_name='Название'
    )
    desc = models.TextField(
        max_length=500,
        help_text="Описание товара",
        verbose_name='Описание'
    )
    composition = models.TextField(
        max_length=500,
        help_text="Состав товара. Можно оставить пустым",
        null=True,
        blank=True,
        verbose_name='Состав'
    )
    price = models.FloatField(
        max_length=10,
        help_text="Базовая цена товара",
        verbose_name='Начальная цена'
    )
    price_old = models.FloatField(
        max_length=10,
        help_text="Цена товара со скидкой. Можно оставить пустым",
        null=True,
        blank=True,
        verbose_name='Цена со скидкой'
    )
    image = models.ImageField(
        upload_to='products/',
        verbose_name='Картинка'
    )

    def __str__(self):
        return self.title


