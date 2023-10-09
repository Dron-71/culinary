from rest_framework.pagination import PageNumberPagination


class MainPagePagination(PageNumberPagination):
    """Ограниение на количество объектов на странице."""
    page_size_query_param = "limit"
