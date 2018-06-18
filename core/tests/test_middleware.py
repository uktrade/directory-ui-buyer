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
