# Generated by Django 4.2.5 on 2023-09-29 15:28

import colorfield.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0005_alter_favorite_options_alter_shoppingcart_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=colorfield.fields.ColorField(default='#FF0000', help_text='Цвет тэга', image_field=None, max_length=16, samples=None, unique=True, verbose_name='Цвет тэга'),
        ),
    ]
