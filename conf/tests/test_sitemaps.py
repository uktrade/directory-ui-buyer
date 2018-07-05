import http

from django.urls import reverse


def test_sitemaps_200(client):
    url = reverse('sitemap')

    response = client.get(url)

    assert response.status_code == http.client.OK
