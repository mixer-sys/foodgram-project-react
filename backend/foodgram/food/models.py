from django.db import models
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        'Название тэга',
        max_length=150,
        unique=True,
    )
    color = models.CharField(
        'Цвет тэга',
        max_length=16,
        unique=True
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
        # ordering = ('-year',)
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
        #  related_name='recipes',
        through='RecipeTag'
    )
    image = models.ImageField(
        upload_to='recipe/images/',
    )
    name = models.CharField(
        'Название',
        max_length=200,
        help_text='Название рецепта'
    )
    text = models.TextField(
        'Описание',
        help_text='Описание рецепта',

    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время',
        help_text='Время приготовления (в минутах)'
    )
    ingredient = models.ManyToManyField(
        'Ingredient',
        verbose_name='Ингредиенты',
        through='RecipeIngredient',
        #  related_name='recipes'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ('pub_date',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='ingredients',

    )
    ingredient = models.ForeignKey(
        'Ingredient',
        on_delete=models.CASCADE,
        related_name='recipes'
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
        on_delete=models.CASCADE,
        related_name='tags',
        blank=True,
        null=True,
    )
    tag = models.ForeignKey(
        'Tag',
        on_delete=models.CASCADE,
        related_name='recipes'
    )

    class Meta:
        # ordering = ('-year',)
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
        help_text='Количество ингредиентов'
    )

    class Meta:
        # ordering = ('-year',)
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='favorites'
    )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shoppingcartrecipes'
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name="shoppingcarts"
    )
