import http
import logging

from directory_api_client.client import DirectoryAPIClient
from directory_validators.constants import choices
import requests

from django.conf import settings

logger = logging.getLogger(__name__)

api_client = DirectoryAPIClient(
    base_url=settings.API_CLIENT_BASE_URL,
    api_key=settings.API_CLIENT_KEY,
)

EMPLOYEE_CHOICES = {key: value for key, value in choices.EMPLOYEES}
SECTOR_CHOICES = {key: value for key, value in choices.COMPANY_CLASSIFICATIONS}


def get_referrer_from_request(request):
    # TODO: determine what source led the user to the export directory
    # if navigating internally then return None (ticket ED-138)
    return 'aaa'


def halt_validation_on_failure(*validators):
    """
    Django runs all validators on a field and shows all errors. Sometimes this
    is undesirable: we may want the validators to stop on the first error.

    """
    def inner(value):
        for validator in validators:
            validator(value)
    inner.inner_validators = validators
    return [inner]


def get_company_name(number):
    try:
        response = api_client.company.retrieve_companies_house_profile(number)
    except requests.exceptions.RequestException:
        logger.exception('Unable to get name for "{0}".'.format(number))
    else:
        if response.status_code == http.client.OK:
            return response.json()['company_name']
        else:
            logger.error('Unable to get name for "{0}". Status "{1}".'.format(
                number, response.status_code
            ))


def user_has_company(sso_user_id):
    response = api_client.user.retrieve_profile(
        sso_id=sso_user_id
    )

    if response.ok:
        has_company = bool(response.json()['company'])
    else:
        has_company = False

    return has_company


def get_employees_label(employees_value):
    if not employees_value:
        return employees_value
    return EMPLOYEE_CHOICES[employees_value]


def get_sectors_labels(sectors_values):
    if not sectors_values:
        return sectors_values
    return [SECTOR_CHOICES[sector_value] for sector_value in sectors_values]
