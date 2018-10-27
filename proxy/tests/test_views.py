import json
import http
import urllib3
from unittest.mock import ANY, call, patch

from django.core.urlresolvers import reverse

import pytest

from proxy import views


@pytest.mark.parametrize('_upstream', ('http://www.e.co/', 'http://www.e.co'))
@patch('urllib3.poolmanager.PoolManager.urlopen')
def test_trailing_slash_upstream(mock_urlopen, _upstream, rf):
    class TestProxyView(views.BaseProxyView):
        upstream = _upstream

    mock_urlopen.return_value = urllib3.response.HTTPResponse(
        body=json.dumps({'key': 'value'}),
        headers={
            'Content-Type': 'application/json', 'Content-Length': '2'
        },
        status=200,
    )

    request = rf.get('/thing')
    view = TestProxyView.as_view()
    view(request)

    assert mock_urlopen.call_args == call(
        'GET',
        'http://www.e.co/thing',
        body=b'',
        decode_content=False,
        headers={
            'X-Forwarded-Host': 'testserver',
            'X-Signature': ANY,
            'Cookie': ''
        },
        preload_content=False,
        redirect=False,
        retries=None
    )


@patch('urllib3.poolmanager.PoolManager.urlopen')
def test_handles_http_error(mock_urlopen, rf, caplog):
    class TestProxyView(views.BaseProxyView):
        pass

    mock_urlopen.side_effect = error = urllib3.exceptions.HTTPError('oops')

    request = rf.get('/thing')
    view = TestProxyView.as_view()
    with pytest.raises(urllib3.exceptions.HTTPError):
        view(request)

    log = caplog.records()[-1]

    assert log.levelname == 'ERROR'
    assert log.msg == error


supplier_company_url = reverse(
    'api-external-company', kwargs={'path': '/supplier/company/'}
)
supplier_url = reverse(
    'api-external-supplier', kwargs={'path': '/external/supplier/'}
)
supplier_sso_url = reverse(
    'api-external-supplier-sso', kwargs={'path': '/external/supplier-sso/'}
)


urls = (
    supplier_company_url, supplier_url, supplier_sso_url
)

test_names = (
    'external company view',
    'external supplier view',
    'external sso id view',
)


@pytest.mark.parametrize('url', urls, ids=test_names)
def test_proxy_api_view_bad_signature(url, client):
    with patch(
            'conf.signature.external_api_checker.test_signature'
    ) as mock_test_signature:
        mock_test_signature.return_value = False

        response = client.get(url)

        assert response.status_code == http.client.FORBIDDEN


@pytest.mark.parametrize('url', urls, ids=test_names)
def test_proxy_api_view_rejects_unsafe_methods(url, client):
    with patch(
            'conf.signature.external_api_checker.test_signature'
    ) as mock_test_signature:
        mock_test_signature.return_value = True

        unsafe_methods = [client.delete, client.post, client.patch, client.put]

        for unsafe_method in unsafe_methods:
            response = unsafe_method(url)
            assert response.status_code == http.client.METHOD_NOT_ALLOWED


@pytest.mark.parametrize('url', urls, ids=test_names)
def test_proxy_api_view_accepts_get(url, client):
    with patch(
            'conf.signature.external_api_checker.test_signature'
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

        response = client.get(url)

        assert response.json() == proxied_content
        assert 'X-Forwarded-Host' not in mock_urlopen.call_args[1]['headers']


DIRECTORY_API_URL = reverse('directory-api', kwargs={'path': '/anything/'})


def test_directory_api_view_bad_signature(client, settings):
    settings.FEATURE_FLAGS['DIRECTORY_API_ON'] = True

    with patch(
            'conf.signature.external_api_checker.test_signature'
    ) as mock_test_signature:
        mock_test_signature.return_value = False

        response = client.get(DIRECTORY_API_URL)

        assert response.status_code == http.client.FORBIDDEN


def test_directory_api_view_does_not_reject_unsafe_methods(client, settings):
    settings.FEATURE_FLAGS['DIRECTORY_API_ON'] = True

    with patch(
            'conf.signature.external_api_checker.test_signature'
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

        unsafe_methods = [client.delete, client.post, client.patch, client.put]

        for unsafe_method in unsafe_methods:
            response = unsafe_method(DIRECTORY_API_URL)
            assert response.status_code != http.client.METHOD_NOT_ALLOWED


def test_directory_api_view_accepts_get(client, settings):
    settings.FEATURE_FLAGS['DIRECTORY_API_ON'] = True

    with patch(
            'conf.signature.external_api_checker.test_signature'
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

        response = client.get(DIRECTORY_API_URL)

        assert response.json() == proxied_content
        assert 'X-Forwarded-Host' not in mock_urlopen.call_args[1]['headers']


def test_directory_api_view_turned_off(client, settings):
    settings.FEATURE_FLAGS['DIRECTORY_API_ON'] = False

    response = client.get(DIRECTORY_API_URL)

    assert response.status_code == http.client.NOT_FOUND
