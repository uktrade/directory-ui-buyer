import http
import json
import pytest
from unittest.mock import patch
import urllib3

from django.core.urlresolvers import reverse

data = (
    ('api-external-company', ),
    ('api-external-supplier',)
)

ids = (
    'external company view',
    'external supplier view'
)


@pytest.mark.parametrize(('view_name',), data, ids=ids)
def test_proxy_api_view_bad_signature(view_name, client):
    with patch(
            'ui.signature.external_api_checker.test_signature'
    ) as mock_test_signature:
        mock_test_signature.return_value = False

        url = reverse(view_name, kwargs={'sso_id': 2})

        response = client.get(url)

        assert response.status_code == http.client.FORBIDDEN


@pytest.mark.parametrize(('view_name',), data, ids=ids)
def test_proxy_api_view_rejects_unsafe_methods(view_name, client):
    with patch(
            'ui.signature.external_api_checker.test_signature'
    ) as mock_test_signature:
        mock_test_signature.return_value = True

        url = reverse(view_name, kwargs={'sso_id': 2})

        unsafe_methods = [client.delete, client.post, client.patch, client.put]

        for unsafe_method in unsafe_methods:
            response = unsafe_method(url)
            assert response.status_code == http.client.METHOD_NOT_ALLOWED


@pytest.mark.parametrize(('view_name',), data, ids=ids)
def test_proxy_api_view_accepts_get(view_name, client):
    with patch(
            'ui.signature.external_api_checker.test_signature'
    ) as mock_test_signature, patch(
            'urllib3.poolmanager.PoolManager.urlopen') as mock_urlopen:
        proxied_content = {'key': 'value'}
        mock_test_signature.return_value = True
        mock_urlopen.return_value = urllib3.response.HTTPResponse(
            body=json.dumps(proxied_content),
            headers={'Content-Type': 'application/json',
                     'Content-Length': '2'},
            status=http.client.OK,
        )

        url = reverse(view_name, kwargs={'sso_id': 2})

        response = client.get(url)

        assert response.json() == proxied_content
        assert 'X-Forwarded-Host' not in mock_urlopen.call_args[1]['headers']
