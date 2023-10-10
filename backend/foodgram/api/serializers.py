import base64

from django.db import transaction
from django.core.files.base import ContentFile
from django.forms.models import model_to_dict
from rest_framework import serializers

from foodgram.settings import (
    MAX_INGREDIENTS_AMOUNT, MIN_INGREDIENTS_AMOUNT,
    MIN_COOKING_TIME, MAX_COOKING_TIME
)
from food.models import Favorite, Ingredient, Recipe
from food.models import RecipeIngredient, RecipeTag, ShoppingCart, Tag
from users.models import User
from users.serializers import UserSerializer

REQUIRED_INGREDIENTS_ERROR = 'Требуются ингредиенты'
REQUIRED_TAGS_ERROR = 'Требуются тэги'
REQUIRED_IMAGE_ERROR = 'Требуется изображение'
NO_SUCH_INGREDIENTS_ERROR = 'Нет такого ингредиета'
FEW_INGREDIENTS_ERROR = ('Количество ингредиента должно быть'
                         f' больше {MIN_INGREDIENTS_AMOUNT}')
MANY_INGREDIENTS_ERROR = ('Количество ингредиента должно быть'
                          f' меньше {MAX_INGREDIENTS_AMOUNT}')
NOT_UNIQUE_INGREDIENTS_ERROR = 'Ингредиенты должны быть уникальными'
NOT_UNIQUE_TAGS_ERROR = 'Тэги должны быть уникальными'
COOKING_TIME_ERROR = ('Время приготовления должно быть больше'
                      f' {MIN_COOKING_TIME}'
                      f' и меньше {MAX_COOKING_TIME}')


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='image.' + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class TagPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def to_representation(self, value):
        return model_to_dict(value.tag)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def to_representation(self, value):
        return model_to_dict(value.ingredient)


class IngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')

    def to_representation(self, value):
        return model_to_dict(value.ingredient)

    def validate_id(self, value):
        if not Ingredient.objects.filter(id=value).exists():
            raise serializers.ValidationError(NO_SUCH_INGREDIENTS_ERROR)
        return value

    def validate_amount(self, value):
        if value < MIN_INGREDIENTS_AMOUNT:
            raise serializers.ValidationError(FEW_INGREDIENTS_ERROR)
        if value > MAX_INGREDIENTS_AMOUNT:
            raise serializers.ValidationError(MANY_INGREDIENTS_ERROR)
        return value


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagPrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    ingredients = IngredientPrimaryKeyRelatedField(
        many=True, queryset=Ingredient.objects.all(),
    )
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )
    image = Base64ImageField(allow_null=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')
        extra_kwargs = {'ingredients': {'required': True}}

    def get_is_favorited(self, obj):
        if self.context.get('request').user.id is None:
            return False
        return Favorite.objects.filter(
            recipe_id=obj.id,
            user=self.context.get('request').user
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        if self.context.get('request').user.id is None:
            return False
        return ShoppingCart.objects.filter(
            recipe_id=obj.id,
            user=self.context.get('request').user
        ).exists()


class RecipeCreateSerializer(RecipeSerializer):
    ingredients = IngredientCreateSerializer(many=True)

    @transaction.atomic
    def create(self, validated_data):
        if 'ingredients' not in validated_data:
            raise serializers.ValidationError(REQUIRED_INGREDIENTS_ERROR)
        ingredients = validated_data.pop('ingredients')
        if 'tags' not in validated_data:
            raise serializers.ValidationError(REQUIRED_TAGS_ERROR)
        tags = validated_data.pop('tags')
        if 'image' not in validated_data:
            raise serializers.ValidationError(REQUIRED_IMAGE_ERROR)
        image = validated_data.pop('image')
        recipe, _ = Recipe.objects.get_or_create(**validated_data)
        recipe.image = image
        recipe.save()
        for tag in tags:
            tag, _ = RecipeTag.objects.get_or_create(
                recipe=recipe, tag=tag
            )
        for ingredient in ingredients:
            id = ingredient.get('id')
            amount = ingredient.get('amount')
            table_ingredient = Ingredient.objects.get(id=id)
            ingredient, _ = Ingredient.objects.get_or_create(
                name=table_ingredient.name,
                measurement_unit=table_ingredient.measurement_unit,
                amount=amount
            )
            recipe_ingredient, _ = RecipeIngredient.objects.get_or_create(
                recipe=recipe, ingredient=ingredient
            )
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        recipe = Recipe.objects.get(id=instance.id)
        validated_data['id'] = instance.id
        validated_data['image'] = recipe.image
        recipe.delete()
        return self.create(validated_data)

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(REQUIRED_INGREDIENTS_ERROR)
        keys = list()
        for ingredient in value:
            keys.append(ingredient.get('id'))
        if len(keys) > len(set(keys)):
            raise serializers.ValidationError(NOT_UNIQUE_INGREDIENTS_ERROR)
        return value

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(REQUIRED_TAGS_ERROR)
        keys = list()
        for tag in value:
            keys.append(tag.id)
        if len(keys) > len(set(keys)):
            raise serializers.ValidationError(NOT_UNIQUE_TAGS_ERROR)
        return value

    def validate_cooking_time(self, value):
        if not (MAX_COOKING_TIME > value > MIN_COOKING_TIME):
            raise serializers.ValidationError(
                COOKING_TIME_ERROR)
        return value


class RecipeSmallSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField(
        method_name='get_recipes'
    )
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count'
    )

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscribed', 'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        return True

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        recipes_limit = (self._context.get('recipes_limit'))
        recipes = obj.recipes.all()[:recipes_limit]
        return RecipeSmallSerializer(recipes, many=True).data
