from rest_framework.pagination import PageNumberPagination

from .constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE


class DefaultPagination(PageNumberPagination):
    """Default paginator: small page size to make paging visible in demos."""

    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = "page_size"
    max_page_size = MAX_PAGE_SIZE
