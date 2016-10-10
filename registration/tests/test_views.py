import http
from unittest import mock

import pytest

from django.core.urlresolvers import reverse

from registration.clients.directory_api import api_client
from registration.constants import SESSION_KEY_REFERRER
from registration.views import EmailConfirmationView, RegistrationView


def test_email_confirm_missing_confirmation_code(rf):
    view = EmailConfirmationView.as_view()
    request = rf.get(reverse('confirm-email'))
    response = view(request)
    assert response.status_code == http.client.OK
    assert response.template_name == EmailConfirmationView.failure_template


@mock.patch.object(api_client, 'confirm_email', return_value=False)
def test_email_confirm_invalid_confirmation_code(mock_confirm_email, rf):
    view = EmailConfirmationView.as_view()
    request = rf.get(reverse('confirm-email'), {'confirmation_code': 123})
    response = view(request)
    assert mock_confirm_email.called_with(123)
    assert response.status_code == http.client.OK
    assert response.template_name == EmailConfirmationView.failure_template


@mock.patch.object(api_client, 'confirm_email', return_value=True)
def test_email_confirm_valid_confirmation_code(mock_confirm_email, rf):
    view = EmailConfirmationView.as_view()
    request = rf.get(reverse('confirm-email'), {'confirmation_code': 123})
    response = view(request)
    assert mock_confirm_email.called_with(123)
    assert response.status_code == http.client.OK
    assert response.template_name == EmailConfirmationView.success_template


@pytest.mark.django_db
def test_registration_view_includes_referrer(client, rf):
    request = rf.get(reverse('register'))
    request.session = client.session
    request.session[SESSION_KEY_REFERRER] = 'google'

    form_pair = RegistrationView.form_list[2]
    view = RegistrationView.as_view(form_list=(form_pair,))
    response = view(request)

    initial = response.context_data['form'].initial
    assert form_pair[0] == 'user'
    assert initial['referrer'] == 'google'
