import base64

from django.core.files.base import ContentFile
from django.forms.models import model_to_dict
from rest_framework import serializers
from food.models import Favorite, Ingredient, Recipe
from food.models import RecipeIngredient, RecipeTag, ShoppingCart, Tag
from users.models import User
from users.serializers import UserSerializer


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


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


class TagPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def to_representation(self, value):
        return model_to_dict(value.tag)


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagPrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = RecipeIngredientSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        if self.context.get('request').user.id is None:
            return False
        return Favorite.objects.filter(
            recipe_id=obj.id, user=self.context.get('request').user).exists()

    def get_is_in_shopping_cart(self, obj):
        if self.context.get('request').user.id is None:
            return False
        return ShoppingCart.objects.filter(
            recipe_id=obj.id, user=self.context.get('request').user).exists()

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        image = validated_data.pop('image')
        recipe, status = Recipe.objects.get_or_create(**validated_data)
        recipe.image = image
        recipe.save()
        RecipeTag.objects.filter(recipe=recipe).delete()
        for tag in tags:
            RecipeTag(recipe=recipe, tag=tag).save()

        RecipeIngredient.objects.filter(recipe=recipe).delete()
        for ingredient in ingredients:
            id = ingredient.get('id')
            amount = ingredient.get('amount')
            RecipeIngredient.objects.get_or_create(
                ingredient_id=id, recipe=recipe,
                amount=amount
            )
        return recipe

    def update(self, instance, validated_data):

        return self.create(validated_data)


class RecipeSmallSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    recipes = RecipeSmallSerializer(many=True)
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

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
