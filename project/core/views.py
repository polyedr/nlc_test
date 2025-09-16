from __future__ import annotations

from typing import Type

from rest_framework import mixins, viewsets
from rest_framework.response import Response

from .constants import ALLOWED_CONTENT_MODELS, APP_LABEL_CORE
from .models import Page, PageContent
from .serializers import PageDetailSerializer, PageListSerializer
from .tasks import increment_counters_async


class PageViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """API viewset for listing and retrieving pages.
    On detail view, increments counters of attached content via Celery task.
    """

    queryset = Page.objects.all().prefetch_related("contents__content_type")
    serializer_class = PageListSerializer

    def get_serializer_class(self) -> Type[PageListSerializer | PageDetailSerializer]:
        return PageDetailSerializer if self.action == "retrieve" else PageListSerializer

    def retrieve(self, request, *args, **kwargs) -> Response:
        page: Page = self.get_object()
        data = self.get_serializer(page).data

        # Produce only (content_type_id, object_id) pairs for core models in support
        content_pairs = list(
            PageContent.objects.filter(
                page=page,
                content_type__app_label=APP_LABEL_CORE,
                content_type__model__in=ALLOWED_CONTENT_MODELS,
            ).values_list("content_type_id", "object_id")
        )

        if content_pairs:
            increment_counters_async(content_pairs)

        return Response(data)
