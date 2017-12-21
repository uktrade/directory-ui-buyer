from unittest.mock import patch


from django.core.urlresolvers import reverse


@patch(
    'healthcheck.backends.SigngleSignOnBackend.check_status', return_value=True
)
def test_single_sign_on(mock_check_status, client, settings):
    response = client.get(
        reverse('healthcheck-single-sign-on'),
        {'token': settings.HEALTH_CHECK_TOKEN},
    )

    assert response.status_code == 200
    assert mock_check_status.call_count == 1


@patch(
    'healthcheck.backends.APIBackend.check_status', return_value=True
)
def test_api(mock_check_status, client, settings):
    response = client.get(
        reverse('healthcheck-api'),
        {'token': settings.HEALTH_CHECK_TOKEN},
    )

    assert response.status_code == 200
    assert mock_check_status.call_count == 1
