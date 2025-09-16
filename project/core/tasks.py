from __future__ import annotations

from typing import Dict, Iterable, List, Tuple, Type

from celery import shared_task

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import F


@shared_task
def increment_counters_task(pairs: List[Tuple[int, int]]) -> None:
    """Celery task to atomically increment `counter` fields for given objects."""
    by_ct: Dict[int, List[int]] = {}
    for ct_id, obj_id in pairs:
        by_ct.setdefault(ct_id, []).append(obj_id)

    for ct_id, ids in by_ct.items():
        model: Type[models.Model] | None = ContentType.objects.get_for_id(
            ct_id
        ).model_class()
        # Skip invalid content types or models without `counter`
        if model is None or not hasattr(model, "counter"):
            continue
        model.objects.filter(id__in=ids).update(counter=F("counter") + 1)


def increment_counters_async(pairs: Iterable[Tuple[int, int]]) -> None:
    """Helper to enqueue the Celery task for counter increments."""
    items = list(pairs)
    try:
        increment_counters_task.delay(items)
    except Exception:
        # Fallback to synchronous execution if broker is unavailable
        increment_counters_task(items)
