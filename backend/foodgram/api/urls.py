from django.urls import path, include
from rest_framework.routers import SimpleRouter
from api.views import (
    APITag, RecipeViewSet,
    APIIngredient,
    APIFavorite,
    APIShoppingCart
)
from users.views import APISubscription

app_name = 'api'

router_api = SimpleRouter()
router_api.register(r'recipes', RecipeViewSet)

urlpatterns = [
    path('ingredients/', APIIngredient.as_view(), name='ingredients'),
    path('ingredients/<int:ingredient_id>/', APIIngredient.as_view(),
         name='ingredient_detail'),
    path('tags/', APITag.as_view(), name='tags'),
    path('tags/<int:tag_id>/', APITag.as_view(), name='tag_detail'),
    path('users/subscriptions/', APISubscription.as_view(),
         name='subscriptions'),
    path('users/<int:user_id>/subscribe/', APISubscription.as_view(),
         name='subscribe'),
    path('recipes/<int:recipe_id>/favorite/', APIFavorite.as_view(),
         name='favorite'),
    path('recipes/<int:recipe_id>/shopping_cart/', APIShoppingCart.as_view(),
         name='shopping_cart'),
    path('recipes/download_shopping_cart/', APIShoppingCart.as_view(),
         name='download_shopping_cart'),
    path('', include('djoser.urls')),
    path('', include(router_api.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
