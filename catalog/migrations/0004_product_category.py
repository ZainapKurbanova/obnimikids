# Generated by Django 5.1.6 on 2025-06-01 23:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0003_product_image_file_alter_product_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.CharField(choices=[('children_1_6', 'Дети 1-6 лет'), ('babies_3_12', 'Малыши (3 – 12 месяцев)')], default='children_1_6', max_length=20, verbose_name='Категория'),
        ),
    ]
