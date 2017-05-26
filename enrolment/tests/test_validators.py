import http
import pytest
from unittest.mock import Mock, patch

from django.forms import ValidationError

from requests.exceptions import HTTPError

from enrolment import validators


@patch.object(validators.api_client.company, 'validate_company_number')
def test_validate_company_unique_invalid(mock_validate_company_number):
    error = 'Already registered. Please login.'
    mock_validate_company_number.return_value = Mock(
        status_code=http.client.BAD_REQUEST,
        json=lambda: {'number': [error]}
    )
    with pytest.raises(ValidationError, message=error):
        validators.company_unique('01245678')


@patch.object(validators.api_client.company, 'validate_company_number')
def test_validate_company_unique_valid(mock_validate_company_number):
    mock_validate_company_number.return_value = Mock(
        status_code=http.client.OK
    )
    assert validators.company_unique('01245678') is None


@patch(
    'enrolment.helpers.get_company_from_companies_house',
    Mock(return_value={
        'company_name': 'company_name',
        'company_status': 'active',
    })
)
def test_validate_company_number_present_and_active_valid():
    assert validators.company_number_present_and_active('01245678') is None


@patch(
    'enrolment.helpers.get_company_from_companies_house',
    Mock(return_value={
        'company_name': 'company_name',
        'company_status': 'inactive',
    })
)
def test_validate_company_number_present_and_active_invalid():

    with pytest.raises(
            ValidationError, message=validators.MESSAGE_COMPANY_NOT_ACTIVE
    ):
        validators.company_number_present_and_active('01245678')


@patch(
    'enrolment.helpers.get_company_from_companies_house',
    Mock(side_effect=HTTPError(
        response=Mock(status_code=http.client.INTERNAL_SERVER_ERROR))
    )
)
def test_validate_company_number_present_and_active_server_error():
    with pytest.raises(
            ValidationError, message=validators.MESSAGE_COMPANY_NOT_ACTIVE
    ):
        validators.company_number_present_and_active('01245678')


@patch(
    'enrolment.helpers.get_company_from_companies_house',
    Mock(side_effect=HTTPError(
        response=Mock(status_code=http.client.NOT_FOUND))
    )
)
def test_validate_company_number_present_and_active_not_found():
    with pytest.raises(
            ValidationError, message=validators.MESSAGE_COMPANY_NOT_FOUND
    ):
        validators.company_number_present_and_active('01245678')
