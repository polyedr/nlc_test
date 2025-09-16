from rest_framework import mixins, viewsets
from rest_framework.response import Response

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

    def get_serializer_class(self):
        return PageDetailSerializer if self.action == "retrieve" else PageListSerializer

    def retrieve(self, request, *args, **kwargs):
        page = self.get_object()
        data = self.get_serializer(page).data
        pairs = list(
            PageContent.objects.filter(page=page).values_list(
                "content_type_id", "object_id"
            )
        )
        if pairs:
            increment_counters_async(pairs)
        return Response(data)
