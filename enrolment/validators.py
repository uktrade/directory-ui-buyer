# these are validators that only the UI needs. Put shared validators in
# directory-validators
import http

from django.forms import ValidationError

from requests.exceptions import RequestException

from api_client import api_client
from enrolment import helpers


MESSAGE_COMPANY_NOT_ACTIVE = 'Company not active.'
MESSAGE_COMPANY_NOT_FOUND = 'Company not found. Please check the number.'
MESSAGE_COMPANY_ERROR = 'Error. Please try again later.'


def company_unique(value):
    # checks "is the company already registered?"
    response = api_client.company.validate_company_number(value)
    if response.status_code != http.client.OK:
        if response.status_code == http.client.BAD_REQUEST:
            raise ValidationError(response.json()['number'][0])
        else:
            raise ValidationError(MESSAGE_COMPANY_ERROR)


def company_active(value):
    if value != 'active':
        raise ValidationError(MESSAGE_COMPANY_NOT_ACTIVE)


def company_number_present_and_active(value):
    try:
        company = helpers.get_company_from_companies_house(
            company_number=value
        )
    except RequestException as error:
        if error.response and error.response.status_code == 404:
            raise ValidationError(MESSAGE_COMPANY_NOT_FOUND)
        else:
            raise ValidationError(MESSAGE_COMPANY_ERROR)
    else:
        # Sometimes CH response does not contain company_status - we treat
        # these as inactive
        company_active(company.get('company_status'))


def email_address(value):
    # checks "is email address already registered?"
    response = api_client.supplier.validate_email_address(value)
    if response.status_code == http.client.BAD_REQUEST:
        raise ValidationError(response.json()['company_email'][0])
