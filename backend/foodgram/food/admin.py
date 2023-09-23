from django.contrib import admin
from django.db import models
from django.forms import Textarea

from food.models import (
    Tag, Recipe, Ingredient, RecipeTag, RecipeIngredient, Favorite,
    ShoppingCart
)
from users.models import (
    Subscription, User
)


class ViewSettings(admin.ModelAdmin):
    list_per_page = 10
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 5, 'cols': 45})},
    }


class TagAdmin(ViewSettings):
    list_display = [field.name for field in Tag._meta.fields]
    empty_value_display = '-пусто-'


class RecipeAdmin(ViewSettings):
    list_display = [field.name for field in Recipe._meta.fields]
    list_filter = ['tag', 'author', 'name']
    empty_value_display = '-пусто-'


class IngredientAdmin(ViewSettings):
    list_display = [field.name for field in Ingredient._meta.fields]
    empty_value_display = '-пусто-'
    list_filter = ['name', ]


class RecipeIngredientAdmin(ViewSettings):
    list_display = [field.name for field in RecipeIngredient._meta.fields]
    empty_value_display = '-пусто-'


class RecipeTagAdmin(ViewSettings):
    list_display = [field.name for field in RecipeTag._meta.fields]
    empty_value_display = '-пусто-'


class FavoriteAdmin(ViewSettings):
    list_display = [field.name for field in Favorite._meta.fields]
    empty_value_display = '-пусто-'


class ShoppingCartAdmin(ViewSettings):
    list_display = [field.name for field in ShoppingCart._meta.fields]
    empty_value_display = '-пусто-'


class SubscriptionAdmin(ViewSettings):
    list_display = [field.name for field in Subscription._meta.fields]
    empty_value_display = '-пусто-'


class UserAdmin(ViewSettings):
    list_display = [field.name for field in User._meta.fields]
    empty_value_display = '-пусто-'
    list_filter = ['username', 'email']


admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(RecipeTag, RecipeTagAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(User, UserAdmin)
