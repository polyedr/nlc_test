# Fixtures
import pytest
from rest_framework.test import APIClient

from core.models import Audio, Page, Video


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def page_factory():
    def create(**kwargs):
        return Page.objects.create(title=kwargs.get("title", "Page"))

    return create


@pytest.fixture
def video_factory():
    def create(**kwargs):
        return Video.objects.create(
            title=kwargs.get("title", "Video"),
            counter=kwargs.get("counter", 0),
            video_url=kwargs.get("video_url", "https://example.com/v.mp4"),
            subtitles_url=kwargs.get("subtitles_url", "https://example.com/v.vtt"),
        )

    return create


@pytest.fixture
def audio_factory():
    def create(**kwargs):
        return Audio.objects.create(
            title=kwargs.get("title", "Audio"),
            counter=kwargs.get("counter", 0),
            transcript=kwargs.get("transcript", "..."),
        )

    return create
