from colorfield.fields import ColorField

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from users.models import User
from foodgram.settings import (
    MIN_COOKING_TIME, MAX_COOKING_TIME,
    MIN_INGREDIENTS_AMOUNT, MAX_INGREDIENTS_AMOUNT
)


class Tag(models.Model):
    name = models.CharField(
        'Название тэга',
        help_text='Название тэга',
        max_length=150,
        unique=True,
    )
    color = ColorField(
        'Цвет тэга',
        help_text='Цвет тэга',
        max_length=16,
        unique=True,
        default='#FF0000'
    )
    slug = models.SlugField(
        'Идентификатор',
        max_length=50,
        unique=True,
        help_text=('Идентификатор тега; '
                   'разрешены символы латиницы, цифры, '
                   'дефис и подчёркивание.')
    )

    class Meta:
        verbose_name = 'тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        help_text='Автор рецепта',
        related_name='recipes'
    )
    tag = models.ManyToManyField(
        'Tag',
        verbose_name='Тэги',
        help_text='Тэги',
        through='RecipeTag'
    )
    image = models.ImageField(
        'Изображение',
        help_text='Изображение рецепта',
        upload_to='recipe/images/',
        blank=False,
        null=False
    )
    name = models.CharField(
        'Название',
        max_length=200,
        help_text='Название рецепта',
        blank=False
    )
    text = models.TextField(
        'Описание',
        help_text='Описание рецепта',
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время',
        help_text='Время приготовления (в минутах)',
        blank=False,
        validators=(
            MaxValueValidator(MAX_COOKING_TIME),
            MinValueValidator(MIN_COOKING_TIME)
        )
    )
    ingredient = models.ManyToManyField(
        'Ingredient',
        verbose_name='Ингредиенты',
        help_text='Ингредиенты',
        through='RecipeIngredient',
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        help_text='Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name

    def count_in_favorite(self):
        return self.favorites.count()


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        'Recipe',
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='ingredients',

    )
    ingredient = models.ForeignKey(
        'Ingredient',
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='recipes',
    )

    class Meta:
        verbose_name = 'рецепт ингредиент'
        verbose_name_plural = 'Рецепты ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient'
            ),
        )

    def amount(self):
        return self.ingredient.amount


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        'Recipe',
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='tags',
        blank=True,
        null=True,
    )
    tag = models.ForeignKey(
        'Tag',
        verbose_name='Тэг',
        on_delete=models.CASCADE,
        related_name='recipes'
    )

    class Meta:
        verbose_name = 'рецепт тэг'
        verbose_name_plural = 'Рецепты тэги'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'tag'),
                name='unique_recipe_tag'
            ),
        )


class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        max_length=200,
        help_text='Название ингредиента'
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=200,
        help_text='Единица измерения ингредиента'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        help_text='Количество ингредиентов',
        null=True,
        validators=(
            MaxValueValidator(MAX_INGREDIENTS_AMOUNT),
            MinValueValidator(MIN_INGREDIENTS_AMOUNT)
        )
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        'Recipe',
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='favorites'
    )

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='shopping_cart_recipes'
    )
    recipe = models.ForeignKey(
        'Recipe',
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='shopping_carts'
    )

    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'Покупки'
