# Generated by Django 4.2.5 on 2023-09-20 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0006_alter_recipe_tag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(default=None, null=True, upload_to='cats/images/'),
        ),
    ]
