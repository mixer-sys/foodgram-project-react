def get_shopping_cart_txt(shoppingcartrecipes):
    ingredients_amounts = dict()
    ingredients_measurement_unit = dict()
    for shoppingcartrecipe in shoppingcartrecipes:
        recipe = shoppingcartrecipe.recipe
        ingredients = recipe.ingredients.all()
        for recipeingredient in ingredients:
            name = recipeingredient.ingredient.name
            measurement_unit = recipeingredient.ingredient.measurement_unit
            amount = recipeingredient.amount
            if name in ingredients_amounts:
                ingredients_amounts[name] += amount
            else:
                ingredients_amounts[name] = amount
                ingredients_measurement_unit[name] = measurement_unit
    file = ''
    for name in ingredients_amounts:
        measurement_unit = ingredients_measurement_unit.get(name)
        amount = ingredients_amounts.get(name)
        line = f'*** {name} ({measurement_unit}) -- {amount}\n'
        file += line
    return file
