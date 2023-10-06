from django_filters.rest_framework import CharFilter, FilterSet, BooleanFilter

from food.models import Recipe


class RecipeFilterSet(FilterSet):
    tags = CharFilter(method='filter_tags')
    is_favorited = BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = BooleanFilter(method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter_tags(self, qs, name, value):
        params = dict(self.request.query_params)
        tags = params.get('tags')
        return qs.filter(tag__slug__in=tags)

    def filter_is_favorited(self, qs, name, value):
        if self.request.user.id is not None:
            return qs.filter(favorites__user=self.request.user)
        return qs

    def filter_is_in_shopping_cart(self, qs, name, value):
        if self.request.user.id is not None:
            return qs.filter(shoppingcarts__user=self.request.user)
        return qs
