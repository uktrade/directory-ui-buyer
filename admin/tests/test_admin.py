import json
from unittest.mock import call, Mock, patch, ANY
import urllib3

from django.core.urlresolvers import reverse


@patch('urllib3.poolmanager.PoolManager.urlopen')
@patch('ui.signature.external_api_checker.test_signature', Mock)
def test_proxy_admin_base_url(mock_urlopen, client):

    url = reverse('admin_proxy')

    proxied_content = {'key': 'value'}
    mock_urlopen.return_value = urllib3.response.HTTPResponse(
        body=json.dumps(proxied_content),
        headers={
            'Content-Type': 'application/json', 'Content-Length': '2'
        },
        status=200,
    )

    response = client.get(url)

    assert response.json() == proxied_content
    assert mock_urlopen.call_args == call(
        'GET',
        'http://api.trade.great.dev:8000/admin/',
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
@patch('ui.signature.external_api_checker.test_signature', Mock)
def test_proxy_admin_with_path(mock_urlopen, client):

    url = reverse('admin_proxy') + 'some/thing/'

    proxied_content = {'key': 'value'}
    mock_urlopen.return_value = urllib3.response.HTTPResponse(
        body=json.dumps(proxied_content),
        headers={
            'Content-Type': 'application/json', 'Content-Length': '2'
        },
        status=200,
    )

    response = client.get(url)

    assert response.json() == proxied_content
    assert mock_urlopen.call_args == call(
        'GET',
        'http://api.trade.great.dev:8000/admin/some/thing/',
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
@patch('ui.signature.external_api_checker.test_signature', Mock)
def test_proxy_admin_with_path_and_queryparam(mock_urlopen, client):

    url = reverse('admin_proxy') + 'some/thing/?q=test'

    proxied_content = {'key': 'value'}
    mock_urlopen.return_value = urllib3.response.HTTPResponse(
        body=json.dumps(proxied_content),
        headers={
            'Content-Type': 'application/json', 'Content-Length': '2'
        },
        status=200,
    )

    response = client.get(url)

    assert response.json() == proxied_content
    assert mock_urlopen.call_args == call(
        'GET',
        'http://api.trade.great.dev:8000/admin/some/thing/?q=test',
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
