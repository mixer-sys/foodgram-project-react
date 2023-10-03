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


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagPrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    ingredients = IngredientPrimaryKeyRelatedField(
        many=True, queryset=Ingredient.objects.all(),
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
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

    def create(self, validated_data):
        if 'ingredients' not in validated_data:
            raise serializers.ValidationError('No ingredients')
        ingredients = validated_data.pop('ingredients')
        if 'tags' not in validated_data:
            raise serializers.ValidationError('No tags')
        tags = validated_data.pop('tags')
        if 'image' not in validated_data:
            raise serializers.ValidationError('No image')
        image = validated_data.pop('image')
        recipe, status = Recipe.objects.get_or_create(**validated_data)
        recipe.image = image
        recipe.save()
        for tag in tags:
            tag, status = RecipeTag.objects.get_or_create(
                recipe=recipe, tag=tag
            )
        for ingredient in ingredients:
            id = ingredient.get('id')
            amount = ingredient.get('amount')
            table_ingredient = Ingredient.objects.get(id=id)
            ingredient, status = Ingredient.objects.get_or_create(
                name=table_ingredient.name,
                measurement_unit=table_ingredient.measurement_unit,
                amount=amount
            )
            recipe_ingredient, status = RecipeIngredient.objects.get_or_create(
                recipe=recipe, ingredient=ingredient
            )
        return recipe

    def update(self, instance, validated_data):
        return self.create(validated_data)

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError("No ingredients")
        keys = list()
        for ingredient in value:
            if not Ingredient.objects.filter(id=ingredient.get('id')).exists():
                raise serializers.ValidationError("No such ingredient")
            if ingredient.get('amount') < 1:
                raise serializers.ValidationError('Few ingredients')
            keys.append(ingredient.get('id'))
        if len(keys) > len(set(keys)):
            raise serializers.ValidationError('There are not uniq ingredients')
        return value

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError('No tags')
        keys = list()
        for tag in value:
            keys.append(tag.id)
        if len(keys) > len(set(keys)):
            raise serializers.ValidationError('There are not uniq tags')
        return value

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Cooking time should be more than 1")
        return value


class RecipeSmallSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
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

    def get_recipes(self, obj):
        recipes_limit = (self._context.get('recipes_limit'))
        recipes = obj.recipes.all()[:recipes_limit]
        return RecipeSmallSerializer(recipes, many=True).data
