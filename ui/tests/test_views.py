import http
from unittest import mock

from django.core.urlresolvers import reverse

from ui.clients.directory_api import api_client
from ui.views import EmailConfirmationView


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
