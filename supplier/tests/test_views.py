import http
from unittest import mock

from django.core.urlresolvers import reverse

from supplier.views import api_client, SupplierProfileDetailView


@mock.patch.object(api_client.supplier, 'retrieve_profile')
def test_supplier_profile_details_calls_api(mock_retrieve_profile, rf):
    view = SupplierProfileDetailView.as_view()
    request = rf.get(reverse('supplier-detail'))
    request.sso_user = mock.Mock(id=1, email="test@example.com")
    view(request)
    assert mock_retrieve_profile.called_once_with(1)


@mock.patch.object(api_client.supplier, 'retrieve_profile')
def test_supplier_profile_details_exposes_context(mock_retrieve_profile, rf):
    mock_retrieve_profile.return_value = expected_context = {
        'company_email': 'jim@example.com',
        'company_id': '01234567',
        'mobile_number': '02343543333',
    }
    view = SupplierProfileDetailView.as_view()
    request = rf.get(reverse('supplier-detail'))
    request.sso_user = mock.Mock(id=1, email="test@example.com")
    response = view(request)
    assert response.status_code == http.client.OK
    assert response.template_name == [SupplierProfileDetailView.template_name]
    assert response.context_data['supplier'] == expected_context
