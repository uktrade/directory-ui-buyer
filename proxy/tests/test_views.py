import json
from unittest.mock import ANY, call, patch
import urllib3

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

    log = caplog.records[-1]

    assert log.levelname == 'ERROR'
    assert log.msg == error
