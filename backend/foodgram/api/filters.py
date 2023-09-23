from django_filters import FilterSet
from django_filters import filters
from food.models import Recipe


class FooFilter(FilterSet):
    #value = filters.CharFilter(field_name='value', method='filter_value')
    value = filters.BooleanFilter(field_name='is_favorited', method='filter_value')

    def filter_value(self, queryset, name, value):
        return queryset.filter(value=value)

    class Meta:
        model = Recipe
        fields = '__all__'
