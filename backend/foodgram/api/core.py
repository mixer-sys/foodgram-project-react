from django.db.models import Sum


def get_shopping_cart_txt(recipes_ingredients):
    file = ''
    for ingredient_measurement_unit in recipes_ingredients.values(
            'ingredient__name', 'ingredient__measurement_unit').distinct():
        name = ingredient_measurement_unit.get('ingredient__name')
        measurement_unit = ingredient_measurement_unit.get(
            'ingredient__measurement_unit'
        )
        amount_sum = recipes_ingredients.filter(
            ingredient__name=name).aggregate(
                Sum('ingredient__amount')).get('ingredient__amount__sum')
        line = f'*** {name} ({measurement_unit}) -- {amount_sum}\n'
        file += line
    return file
