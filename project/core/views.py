from __future__ import annotations

from typing import Type

from rest_framework import mixins, viewsets
from rest_framework.response import Response

from .models import Page, PageContent
from .serializers import PageDetailSerializer, PageListSerializer


class PageViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
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
        # Only core models (video/audio) — order preserved by PageContent.Meta.ordering
        pairs = list(
            PageContent.objects.filter(page=page).values_list("content_type_id", "object_id")
        )
        if pairs:
            from .tasks import increment_counters_async
            increment_counters_async(pairs)
        return Response(data)
