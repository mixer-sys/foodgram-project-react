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
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    empty_value_display = '-пусто-'
    list_filter = ('measurement_unit',)


class TagAdmin(ViewSettings):
    list_display = [field.name for field in Tag._meta.fields]
    empty_value_display = '-пусто-'


class IngredientInline(admin.TabularInline):
    model = RecipeIngredient


class RecipeAdmin(ViewSettings):
    list_display = [field.name for field in Recipe._meta.fields]
    list_display += ('count_in_favorite', 'ingredients')
    search_fields = ('author__username', 'author__email')
    list_filter = ('tag__slug',)
    inlines = (IngredientInline,)
    empty_value_display = '-пусто-'

    def ingredients(self, obj):
        return ', '.join([p.ingredient.name for p in obj.ingredients.all()])


class RecipeIngredientAdmin(ViewSettings):
    list_display = [field.name for field in RecipeIngredient._meta.fields]
    list_display += ('amount',)
    search_fields = ('recipe__name', 'ingredient__name')
    list_filter = ('recipe__tag__slug',)
    empty_value_display = '-пусто-'


class RecipeTagAdmin(ViewSettings):
    list_display = [field.name for field in RecipeTag._meta.fields]
    search_fields = ('recipe__name',)
    list_filter = ('tag__slug',)
    empty_value_display = '-пусто-'


class FavoriteAdmin(ViewSettings):
    list_display = [field.name for field in Favorite._meta.fields]
    search_fields = ('user__username', 'user__email')
    list_filter = ('recipe__tag__slug',)
    empty_value_display = '-пусто-'


class ShoppingCartAdmin(ViewSettings):
    list_display = [field.name for field in ShoppingCart._meta.fields]
    search_fields = ('user__username', 'user__email')
    list_filter = ('recipe__tag__slug',)
    empty_value_display = '-пусто-'


admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientResourceAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(RecipeTag, RecipeTagAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
