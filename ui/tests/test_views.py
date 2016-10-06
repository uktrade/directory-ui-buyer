import http
from unittest import mock

from django.core.urlresolvers import reverse
from django.test import override_settings

from ui.clients.directory_api import api_client
from ui.views import EmailConfirmationView, IndexView

VALID_REQUEST_DATA = {
    "contact_name": "Test",
    "marketing_source_bank": "",
    "website": "example.com",
    "exporting": "False",
    "phone_number": "",
    "marketing_source": "Social media",
    "opt_in": True,
    "marketing_s ource_other": "",
    "email_address1": "test@example.com",
    "agree_terms": True,
    "company_name": "Example Limited",
    "email_address2": "test@example.com"
}


@override_settings(DATA_SERVER='test')
def test_index_view_create(rf):
    view = IndexView.as_view()
    request = rf.post('/', VALID_REQUEST_DATA)

    response_mock = mock.Mock(status_code=202, ok=True)
    with mock.patch('alice.helpers.rabbit.post', return_value=response_mock):
        response = view(request)

    assert response.url == reverse('thanks')


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
