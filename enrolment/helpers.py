import http
import logging

from directory_api_client.client import DirectoryAPIClient
import requests

from django.conf import settings

logger = logging.getLogger(__name__)

api_client = DirectoryAPIClient(
    base_url=settings.API_CLIENT_BASE_URL,
    api_key=settings.API_CLIENT_KEY,
)


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
