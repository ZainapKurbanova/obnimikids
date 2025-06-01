from django.db import models

class Size(models.Model):
    name = models.CharField(max_length=10, unique=True, verbose_name="Размер")

    class Meta:
        verbose_name = "Размер"
        verbose_name_plural = "Размеры"

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Старая цена")
    image = models.URLField(max_length=500, verbose_name="Ссылка на изображение", blank=True, null=True)
    image_file = models.FileField(upload_to='temp/', verbose_name="Изображение", blank=True, null=True)  # Явно указываем temp/
    sizes = models.ManyToManyField(Size, verbose_name="Размеры", blank=True)
    color = models.CharField(max_length=50, verbose_name="Цвет", default="Не указан")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return f"{self.name} ({self.color})"
