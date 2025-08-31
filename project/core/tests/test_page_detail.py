import pytest
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from core.models import Audio, PageContent, Video


@pytest.mark.django_db
def test_page_detail_increments_counters(
    api_client, page_factory, video_factory, audio_factory, settings
):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    page = page_factory(title="Page")
    v = video_factory(title="V", counter=0)
    a = audio_factory(title="A", counter=1)

    PageContent.objects.create(
        page=page,
        content_type=ContentType.objects.get_for_model(Video),
        object_id=v.id,
        position=1,
    )
    PageContent.objects.create(
        page=page,
        content_type=ContentType.objects.get_for_model(Audio),
        object_id=a.id,
        position=2,
    )

    resp = api_client.get(reverse("page-detail", kwargs={"pk": page.id}))
    assert resp.status_code == 200

    # counters incremented
    v.refresh_from_db()
    a.refresh_from_db()
    assert v.counter == 1
    assert a.counter == 2

    # order and payload
    items = resp.data["items"]
    assert [i["type"] for i in items] == ["video", "audio"]
