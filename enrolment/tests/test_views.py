from unittest import mock

from directory_api_client import api_client
from directory_constants import urls

from django.core.urlresolvers import reverse

from core.tests.helpers import create_response


@mock.patch.object(
    api_client.company, 'retrieve_private_profile',
    mock.Mock(return_value=create_response(404)),
)
def test_landing_page_logged_in(client, user):
    client.force_login(user)

    response = client.get(reverse('index'))

    assert response.status_code == 200
    assert response.context_data['enrolment_url'] == (
        urls.build_great_url('profile/enrol')
    )


def test_landing_page_not_logged_in(client, settings):
    response = client.get(reverse('index'))

    assert response.status_code == 200
    assert response.context_data['enrolment_url'] == (
        settings.SSO_PROXY_LOGIN_URL
    )
