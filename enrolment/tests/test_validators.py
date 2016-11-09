import http
import pytest
from unittest.mock import Mock, patch

from django.forms import ValidationError

from enrolment import validators


@patch.object(validators.api_client.company, 'validate_company_number')
def test_validate_company_number_invalid(mock_validate_company_number):
    error = 'Already registered. Please login.'
    mock_validate_company_number.return_value = Mock(
        status_code=http.client.BAD_REQUEST,
        json=lambda: {'number': [error]}
    )
    with pytest.raises(ValidationError, message=error):
        validators.company_number('01245678')


@patch.object(validators.api_client.company, 'validate_company_number')
def test_validate_company_number_valid(mock_validate_company_number):
    mock_validate_company_number.return_value = Mock(
        status_code=http.client.OK
    )
    assert validators.company_number('01245678') is None


@patch.object(validators.api_client.user, 'validate_email_address')
def test_validate_email_address_invalid(mock_mock_validate_email_address):
    error = 'Already registered. Please login.'
    mock_mock_validate_email_address.return_value = Mock(
        status_code=http.client.BAD_REQUEST,
        json=lambda: {'company_email': [error]}
    )
    with pytest.raises(ValidationError, message=error):
        validators.email_address('01245678')


@patch.object(validators.api_client.user, 'validate_email_address')
def test_validate_email_address_valid(mock_validate_email_address):
    mock_validate_email_address.return_value = Mock(
        status_code=http.client.OK
    )
    assert validators.email_address('01245678') is None


@patch.object(validators.api_client.user, 'validate_mobile_number')
def test_validate_mobile_number_invalid(mock_mock_validate_mobile_number):
    error = 'Already registered. Please login.'
    mock_mock_validate_mobile_number.return_value = Mock(
        status_code=http.client.BAD_REQUEST,
        json=lambda: {'mobile_number': [error]}
    )
    with pytest.raises(ValidationError, message=error):
        validators.mobile_number('01245678')


@patch.object(validators.api_client.user, 'validate_mobile_number')
def test_validate_mobile_number_valid(mock_validate_mobile_number):
    mock_validate_mobile_number.return_value = Mock(
        status_code=http.client.OK
    )
    assert validators.mobile_number('01245678') is None
