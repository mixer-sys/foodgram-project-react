from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from food.models import Tag, Recipe, Ingredient, Favorite, ShoppingCart
from api.serializers import (
    TagSerializer, RecipeSerializer,
    IngredientSerializer, RecipeSmallSerializer,
    RecipeCreateSerializer
)
from api.core import get_shopping_cart_txt
from api.permissions import OwnerOrReadOnly
from users.models import User


class RecipeViewSet(viewsets.ModelViewSet):
    filter_backends = (DjangoFilterBackend, )
    filterset_fields = ('author',)
    permission_classes = (IsAuthenticatedOrReadOnly, OwnerOrReadOnly)
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        params = ((self.request.query_params))
        params = (dict(params))
        tags = params.get('tags')
        is_in_shopping_cart = params.get('is_in_shopping_cart')
        is_favorited = params.get('is_favorited')
        recipes = Recipe.objects.all()
        if tags:
            recipes = Recipe.objects.filter(
                tag__slug__in=tags
            ).distinct()
        if is_in_shopping_cart:
            if self.request.user.id is not None:
                recipes = recipes.filter(
                    shoppingcarts__user=self.request.user)
        if is_favorited:
            if self.request.user.id is not None:
                recipes = recipes.filter(
                    favorites__user=self.request.user)
        return recipes.all()


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
        params = request.query_params
        ingredients = Ingredient.objects.all()
        if params:
            ingredients = ingredients.filter(
                name__startswith=params.get('name')
            )
        serializer = IngredientSerializer(ingredients, many=True)
        if ingredient_id:
            ingredients = get_object_or_404(Ingredient, id=ingredient_id)
            serializer = IngredientSerializer(ingredients)
        return Response(serializer.data)


class APIFavorite(APIView):
    def post(self, request, *args, **kwargs):
        recipe = Recipe.objects.filter(id=kwargs.get('recipe_id'))
        if not recipe.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        recipe = recipe.first()
        favorite = recipe.favorites.filter(user=request.user)
        if favorite.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        Favorite(
            user=request.user, recipe_id=kwargs.get('recipe_id')).save()
        serializer = RecipeSmallSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        recipe = get_object_or_404(Recipe, id=kwargs.get('recipe_id'))
        favorite = recipe.favorites.filter(user=request.user)
        if not favorite.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class APIShoppingCart(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

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
        recipe = Recipe.objects.filter(id=kwargs.get('recipe_id'))
        if not recipe.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        recipe = recipe.first()
        shopping_cart = recipe.shoppingcarts.filter(user=request.user)
        if shopping_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ShoppingCart(
            user=request.user, recipe_id=kwargs.get('recipe_id')).save()
        serializer = RecipeSmallSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        recipe = get_object_or_404(Recipe, id=kwargs.get('recipe_id'))
        if recipe is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        shopping_cart = recipe.shoppingcarts.filter(user=request.user)
        if not shopping_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
