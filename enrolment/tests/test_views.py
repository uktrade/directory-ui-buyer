from unittest import mock

from directory_api_client import api_client

from django.core.urlresolvers import reverse

from core.tests.helpers import create_response


@mock.patch.object(api_client.company, 'profile_retrieve', mock.Mock(return_value=create_response(404)))
def test_landing_page_logged_in(client, user):
    client.force_login(user)

    response = client.get(reverse('index'))

    assert response.status_code == 200
    assert response.context_data['enrolment_url'] == (
        'http://profile.trade.great:8006/profile/enrol/'
        '?business-profile-intent=true'
    )


def test_landing_page_not_logged_in(client, settings):
    response = client.get(reverse('index'))

    assert response.status_code == 200
    assert response.context_data['enrolment_url'] == (
        'http://sso.trade.great:8004/accounts/login/'
        '?next=http%3A//profile.trade.great%3A8006/profile/enrol/'
        '%3Fbusiness-profile-intent%3Dtrue'
    )
