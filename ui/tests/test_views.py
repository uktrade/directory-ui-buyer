from unittest import mock

from django.core.urlresolvers import reverse
from django.test import override_settings

from ui.views import IndexView

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
