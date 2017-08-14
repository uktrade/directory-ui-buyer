from unittest.mock import Mock

import pytest

from django.http import HttpResponse

from ui import middleware


def test_no_cache_middlware_installed(settings):
    assert 'ui.middleware.NoCacheMiddlware' in settings.MIDDLEWARE_CLASSES


def test_no_cache_middlware(rf, settings):
    settings.MIDDLEWARE_CLASSES = []

    with pytest.raises(AssertionError):
        middleware.NoCacheMiddlware()


def test_no_cache_middlware_sso_user(rf):
    request = rf.get('/')
    request.sso_user = Mock()
    response = HttpResponse()

    output = middleware.NoCacheMiddlware().process_response(request, response)

    assert output == response
    assert output['Cache-Control'] == 'no-store, no-cache'


def test_no_cache_middlware_anon_user(rf):
    request = rf.get('/')
    request.sso_user = None
    response = HttpResponse()

    output = middleware.NoCacheMiddlware().process_response(request, response)

    assert output == response
    assert 'Cache-Control' not in output
