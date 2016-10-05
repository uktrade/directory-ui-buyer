import http
from unittest import mock

from django.core.urlresolvers import reverse
from django.test import override_settings

from ui.clients.directory_api import client
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


def test_email_confirm_missing_identifier(rf):
    view = EmailConfirmationView.as_view()
    request = rf.get(reverse('confirm-email'))
    response = view(request)
    assert response.status_code == http.client.FOUND
    assert response.get('Location') == reverse('confirm-email-error')


@mock.patch.object(client, 'acknowledge_email_confirmed',
                   side_effect=client.RemoteError)
def test_email_confirm_invalid_identifier(mock_acknowledge_email_confirmed, rf):
    view = EmailConfirmationView.as_view()
    request = rf.get(reverse('confirm-email'), {'identifier': 123})
    response = view(request)
    assert mock_acknowledge_email_confirmed.called_with(123)
    assert response.status_code == http.client.FOUND
    assert response.get('Location') == reverse('confirm-email-error')


@mock.patch.object(client, 'acknowledge_email_confirmed')
def test_email_confirm_valid_identifier(mock_acknowledge_email_confirmed, rf):
    view = EmailConfirmationView.as_view()
    request = rf.get(reverse('confirm-email'), {'identifier': 123})
    response = view(request)
    assert mock_acknowledge_email_confirmed.called_with(123)
    assert response.status_code == http.client.FOUND
    assert response.get('Location') == reverse('confirm-email-success')
