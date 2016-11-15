# these are validators that only the UI needs. Put shared validators in
# directory-validators
import http

from django.forms import ValidationError

from api_client import api_client


def company_number(value):
    # checks "Is company active?", "does it exist", "is it already registered?"
    response = api_client.company.validate_company_number(value)
    if response.status_code == http.client.BAD_REQUEST:
        raise ValidationError(response.json()['number'][0])


def email_address(value):
    # checks "is email adddress already registered?"
    response = api_client.user.validate_email_address(value)
    if response.status_code == http.client.BAD_REQUEST:
        raise ValidationError(response.json()['company_email'][0])


def mobile_number(value):
    # checks "is phone number already registered?"
    response = api_client.user.validate_mobile_number(value)
    if response.status_code == http.client.BAD_REQUEST:
        raise ValidationError(response.json()['mobile_number'][0])
