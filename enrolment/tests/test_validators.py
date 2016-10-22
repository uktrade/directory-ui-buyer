import http
from unittest.mock import Mock, patch

from enrolment import forms, validators


@patch.object(validators.api_client.company, 'validate_company_number')
def test_company_form_accepts_api_reject(mock_validate_company_number):
    errors = ['Already registered. Please login.']
    mock_validate_company_number.return_value = Mock(
        status_code=http.client.BAD_REQUEST,
        json=lambda: {'number': errors}
    )
    form = forms.CompanyForm(data={'company_number': '01245678'})
    assert form.is_valid() is False
    assert form.errors['company_number'] == errors


@patch.object(validators.api_client.company, 'validate_company_number')
def test_company_form_accepts_api_accept(mock_validate_company_number):
    mock_validate_company_number.return_value = Mock(
        status_code=http.client.OK
    )
    form = forms.CompanyForm(data={'company_number': '01245678'})
    assert form.is_valid() is True
