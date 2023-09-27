from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from food.models import Tag, Recipe, Ingredient, Favorite, ShoppingCart
from food.models import RecipeIngredient
from api.serializers import (
    TagSerializer, RecipeSerializer,
    IngredientSerializer, RecipeSmallSerializer
)
from api.core import get_shopping_cart_txt
from users.models import User


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    #  pagination_class = None
    filterset_fields = ('author',)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        params = ((self.request.query_params))
        tags = params.get('tags')
        is_in_shopping_cart = params.get('is_in_shopping_cart')
        is_favorited = params.get('is_favorited')
        recipes = super().get_queryset()
        if tags:
            recipes = recipes.filter(tag__slug=tags)
        if is_in_shopping_cart:
            if self.request.user.id is not None:
                recipes = recipes.filter(
                    shoppingcarts__user=self.request.user)
        if is_favorited:
            if self.request.user.id is not None:
                recipes = recipes.filter(
                    favorites__user=self.request.user)
        return recipes


class APITag(APIView):
    def get(self, request, tag_id=None):
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        if tag_id:
            tags = get_object_or_404(Tag, id=tag_id)
            serializer = TagSerializer(tags)
        return Response(serializer.data)


class APIIngredient(APIView):
    def get(self, request, ingredient_id=None):
        ingredients = Ingredient.objects.all()
        serializer = IngredientSerializer(ingredients, many=True)
        if ingredient_id:
            ingredients = get_object_or_404(Ingredient, id=ingredient_id)
            serializer = IngredientSerializer(ingredients)
        return Response(serializer.data)


class APIFavorite(APIView):
    def post(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs.get('recipe_id'))
        favorite = recipe.favorites.filter(user=request.user)
        if not favorite.exists():
            Favorite(
                user=request.user, recipe_id=kwargs.get('recipe_id')).save()
        serializer = RecipeSmallSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs.get('recipe_id'))
        favorite = recipe.favorites.filter(user=request.user)
        if favorite.exists():
            favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class APIShoppingCart(APIView):
    def get(self, request, recipe_id=None):
        user = get_object_or_404(User, username=request.user)
        shoppingcartrecipes = user.shoppingcartrecipes.all()
        shopping_cart_txt = get_shopping_cart_txt(shoppingcartrecipes)
        response = HttpResponse(
            shopping_cart_txt, content_type='text/plain; charset=UTF-8')
        response['Content-Disposition'] = (
            'attachment; filename=shoppingcart.txt')
        return response

    def post(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs.get('recipe_id'))
        shopping_cart = recipe.shoppingcarts.filter(user=request.user)
        if not shopping_cart.exists():
            ShoppingCart(
                user=request.user, recipe_id=kwargs.get('recipe_id')).save()
        serializer = RecipeSmallSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs.get('recipe_id'))
        shopping_cart = recipe.shoppingcarts.filter(user=request.user)
        if shopping_cart.exists():
            shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
