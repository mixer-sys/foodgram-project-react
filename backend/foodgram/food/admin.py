from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from django.db import models
from django.forms import Textarea
from food.models import (
    Tag, Recipe, Ingredient, RecipeTag, RecipeIngredient, Favorite,
    ShoppingCart
)


class ViewSettings(admin.ModelAdmin):
    list_per_page = 10
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 5, 'cols': 45})},
    }


class IngredientResource(resources.ModelResource):
    class Meta:
        model = Ingredient


class IngredientResourceAdmin(ImportExportModelAdmin):
    resource_classes = [IngredientResource]
    list_display = ['id', 'name', 'measurement_unit']
    empty_value_display = '-пусто-'
    list_filter = ['name', ]


class TagAdmin(ViewSettings):
    list_display = [field.name for field in Tag._meta.fields]
    empty_value_display = '-пусто-'


class RecipeAdmin(ViewSettings):
    list_display = [field.name for field in Recipe._meta.fields]
    list_display += ['count_in_favorite', ]
    list_filter = ['tag', 'author', 'name']
    empty_value_display = '-пусто-'


class RecipeIngredientAdmin(ViewSettings):
    list_display = [field.name for field in RecipeIngredient._meta.fields]
    list_display += ['amount', ]
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


admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientResourceAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(RecipeTag, RecipeTagAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
