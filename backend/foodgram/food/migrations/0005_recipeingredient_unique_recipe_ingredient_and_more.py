# Generated by Django 4.2.5 on 2023-09-19 19:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0004_remove_recipeingredient_unique_recipe_ingredient_and_more'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='recipeingredient',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredient'), name='unique_recipe_ingredient'),
        ),
        migrations.AddConstraint(
            model_name='recipetag',
            constraint=models.UniqueConstraint(fields=('recipe', 'tag'), name='unique_recipe_tag'),
        ),
    ]
