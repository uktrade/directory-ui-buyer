import http
from unittest import mock

from django.core.urlresolvers import reverse

from user.views import api_client, UserProfileDetailView


@mock.patch.object(api_client.user, 'retrieve_profile')
def test_user_profile_details_calls_api(mock_retrieve_profile, rf):
    view = UserProfileDetailView.as_view()
    request = rf.get(reverse('user-detail'))
    request.sso_user = mock.Mock(id=1, email="test@example.com")
    view(request)
    assert mock_retrieve_profile.called_once_with(1)


@mock.patch.object(api_client.user, 'retrieve_profile')
def test_user_profile_details_exposes_context(mock_retrieve_profile, rf):
    mock_retrieve_profile.return_value = expected_context = {
        'company_email': 'jim@example.com',
        'company_id': '01234567',
        'mobile_number': '02343543333',
    }
    view = UserProfileDetailView.as_view()
    request = rf.get(reverse('user-detail'))
    request.sso_user = mock.Mock(id=1, email="test@example.com")
    response = view(request)
    assert response.status_code == http.client.OK
    assert response.template_name == [UserProfileDetailView.template_name]
    assert response.context_data['user'] == expected_context
