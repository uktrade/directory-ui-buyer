from unittest.mock import Mock, patch

import pytest

from django.forms.fields import Field
from django.core.validators import URLValidator

from company import forms, validators


URL_FORMAT_MESSAGE = URLValidator.message
REQUIRED_MESSAGE = Field.default_error_messages['required']


def test_company_address_verification_required_fields():
    form = forms.CompanyAddressVerificationForm(data={})

    assert form.fields['postal_full_name'].required is True
    assert form.fields['address_confirmed'].required is True


def test_company_address_verification_accepts_valid():
    data = {
        'postal_full_name': 'Jim Example',
        'address_confirmed': True,
    }
    form = forms.CompanyAddressVerificationForm(data=data)

    assert form.is_valid() is True
    assert form.cleaned_data == data


@patch('company.validators.api_client.company.verify_with_code')
def test_company_address_verification_valid_code(mock_verify_with_code):
    mock_verify_with_code.return_value = Mock(ok=False)

    form = forms.CompanyCodeVerificationForm(
        sso_session_id=1,
        data={'code': 'x'*12}
    )

    assert form.is_valid() is False
    assert form.errors['code'] == [validators.MESSAGE_INVALID_CODE]


@patch('company.validators.api_client.company.verify_with_code')
def test_company_address_verification_invalid_code(mock_verify_with_code):
    mock_verify_with_code.return_value = Mock(status_code=200)

    form = forms.CompanyCodeVerificationForm(
        sso_session_id=1,
        data={'code': 'x'*12}
    )

    assert form.is_valid() is True


@patch('company.validators.api_client.company.verify_with_code')
def test_company_address_verification_too_long(mock_verify_with_code):
    mock_verify_with_code.return_value = Mock(status_code=200)

    form = forms.CompanyCodeVerificationForm(
        sso_session_id=1,
        data={'code': 'x'*13}
    )
    expected = 'Ensure this value has at most 12 characters (it has 13).'

    assert form.is_valid() is False
    assert form.errors['code'] == [expected]


@patch('company.validators.api_client.company.verify_with_code')
def test_company_address_verification_too_short(mock_verify_with_code):
    mock_verify_with_code.return_value = Mock(status_code=200)

    form = forms.CompanyCodeVerificationForm(
        sso_session_id=1,
        data={'code': 'x'*11}
    )
    expected = 'Ensure this value has at least 12 characters (it has 11).'

    assert form.is_valid() is False
    assert form.errors['code'] == [expected]


@pytest.mark.parametrize('form_class', [
    forms.AddCollaboratorForm,
    forms.TransferAccountEmailForm,
])
def test_add_collaborator_prevents_sending_to_self(form_class):
    form = form_class(
        sso_email_address='dev@example.com',
        data={'email_address': 'dev@example.com'}
    )

    assert form.is_valid() is False
    assert form.errors['email_address'] == [form.MESSAGE_CANNOT_SEND_TO_SELF]


@pytest.mark.parametrize('form_class', [
    forms.AddCollaboratorForm,
    forms.TransferAccountEmailForm,
])
def test_add_collaborator_allows_sending_to_other(form_class):
    form = form_class(
        sso_email_address='dev@example.com',
        data={'email_address': 'dev+1@example.com'}
    )

    assert form.is_valid() is True
