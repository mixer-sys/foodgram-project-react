# Generated by Django 4.2.5 on 2023-09-27 18:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0003_remove_recipeingredient_unique_recipe_ingredient'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='recipetag',
            name='unique_recipe_tag',
        ),
    ]
