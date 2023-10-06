from rest_framework.pagination import PageNumberPagination


class RecipePageNumberPagination(PageNumberPagination):
    page_size_query_param = 'limit'
