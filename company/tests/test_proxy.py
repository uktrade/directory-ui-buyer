import http
import json
from unittest.mock import patch
import urllib3

from django.core.urlresolvers import reverse


@patch('company.proxy.SignatureRejection.test_signature')
def test_company_private_api_view_bad_signature(mock_test_signature, client):
    mock_test_signature.return_value = False

    url = reverse('api-external-company', kwargs={'sso_id': 2})

    response = client.get(url)

    assert response.status_code == http.client.FORBIDDEN


@patch('company.proxy.SignatureRejection.test_signature')
def test_company_private_api_view_rejects_unsafe_methods(
    mock_test_signature, client
):
    mock_test_signature.return_value = True

    url = reverse('api-external-company', kwargs={'sso_id': 2})

    unsafe_methods = [client.delete, client.post, client.patch, client.put]

    for unsafe_method in unsafe_methods:
        response = unsafe_method(url)
        assert response.status_code == http.client.METHOD_NOT_ALLOWED


@patch('company.proxy.SignatureRejection.test_signature')
@patch('urllib3.poolmanager.PoolManager.urlopen')
def test_company_private_api_view_accepts_get(
    mock_urlopen, mock_test_signature, client
):
    proxied_content = {'key': 'value'}
    mock_test_signature.return_value = True
    mock_urlopen.return_value = urllib3.response.HTTPResponse(
        body=json.dumps(proxied_content),
        headers={'Content-Type': 'application/json', 'Content-Length': '2'},
        status=http.client.OK,
    )

    url = reverse('api-external-company', kwargs={'sso_id': 2})

    response = client.get(url)

    assert response.json() == proxied_content
    assert 'X-Forwarded-Host' not in mock_urlopen.call_args[1]['headers']
