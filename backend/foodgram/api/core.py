from django.db.models import Sum


def get_shopping_cart_txt(recipes_ingredients):
    file = ''
    for recipe_ingredient in recipes_ingredients:
        ingredient = recipe_ingredient.ingredient
        name = ingredient.name
        measurement_unit = ingredient.measurement_unit
        amount_sum = recipes_ingredients.filter(
            ingredient__name=name).aggregate(
                Sum('ingredient__amount')).get('ingredient__amount__sum')
        line = f'*** {name} ({measurement_unit}) -- {amount_sum}\n'
        if line not in file:
            file += line
    return file
