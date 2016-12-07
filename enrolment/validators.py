# these are validators that only the UI needs. Put shared validators in
# directory-validators
import http

from django.forms import ValidationError

from api_client import api_client


MESSAGE_COMPANY_NOT_ACTIVE = 'Company not active.'


def company_unique(value):
    # checks "is the company already registered?"
    response = api_client.company.validate_company_number(value)
    if response.status_code == http.client.BAD_REQUEST:
        raise ValidationError(response.json()['number'][0])


def company_active(value):
    if value != 'active':
        raise ValidationError(MESSAGE_COMPANY_NOT_ACTIVE)


def email_address(value):
    # checks "is email address already registered?"
    response = api_client.supplier.validate_email_address(value)
    if response.status_code == http.client.BAD_REQUEST:
        raise ValidationError(response.json()['company_email'][0])
