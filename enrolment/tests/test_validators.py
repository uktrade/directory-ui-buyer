import http
import pytest
from unittest.mock import Mock, patch

from django.forms import ValidationError

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
