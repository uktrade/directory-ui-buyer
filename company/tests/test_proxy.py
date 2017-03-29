import http
from unittest.mock import patch

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
