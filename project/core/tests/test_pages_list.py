import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_pages_list(api_client, page_factory):
    page_factory(title="First")
    url = reverse("page-list")
    resp = api_client.get(url)
    assert resp.status_code == 200
    assert resp.data["results"][0]["title"] == "First"
    assert "url" in resp.data["results"][0]
