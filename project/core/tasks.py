from typing import Iterable, Tuple

from celery import shared_task
from django.contrib.contenttypes.models import ContentType
from django.db.models import F


@shared_task
def increment_counters_task(pairs: list[tuple[int, int]]):
    """Celery task to atomically increment `counter` fields for given objects."""
    from .models import (  # noqa: F401  (модели нужны только для ContentType)
        Audio,
        Video,
    )

    by_ct: dict[int, list[int]] = {}
    for ct_id, obj_id in pairs:
        by_ct.setdefault(ct_id, []).append(obj_id)
    for ct_id, ids in by_ct.items():
        model = ContentType.objects.get_for_id(ct_id).model_class()
        if model is not None:
            model.objects.filter(id__in=ids).update(counter=F("counter") + 1)


def increment_counters_async(pairs: Iterable[Tuple[int, int]]):
    """Helper to enqueue the Celery task for counter increments."""
    increment_counters_task.delay(list(pairs))
