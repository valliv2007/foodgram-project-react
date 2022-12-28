from rest_framework.pagination import PageNumberPagination


class RecipePagination(PageNumberPagination):
    """Паджинация  для  рецептов"""
    page_size_query_param = 'limit'