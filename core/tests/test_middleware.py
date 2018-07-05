from unittest.mock import Mock

import pytest

from django.http import HttpResponse

from core import middleware


def test_maintenance_mode_middleware_installed(settings):
    expected = 'core.middleware.MaintenanceModeMiddleware'
    assert expected in settings.MIDDLEWARE_CLASSES


def test_maintenance_mode_middleware_feature_flag_on(rf, settings):
    settings.FEATURE_MAINTENANCE_MODE_ENABLED = True
    request = rf.get('/')

    response = middleware.MaintenanceModeMiddleware().process_request(request)

    assert response.status_code == 302
    assert response.url == middleware.MaintenanceModeMiddleware.maintenance_url


def test_maintenance_mode_middleware_feature_flag_off(rf):
    request = rf.get('/')

    response = middleware.MaintenanceModeMiddleware().process_request(request)

    assert response is None


def test_no_cache_middlware_installed(settings):
    assert 'core.middleware.NoCacheMiddlware' in settings.MIDDLEWARE_CLASSES


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


def test_no_cache_middleware_sso_user_not_in_request(rf):
    request = rf.get('/')
    response = HttpResponse()

    output = middleware.NoCacheMiddlware().process_response(request, response)

    assert output == response
    assert 'Cache-Control' not in output
