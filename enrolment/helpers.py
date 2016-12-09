import http
import logging

import requests

from django.conf import settings

from api_client import api_client


COMPANIES_HOUSE_PROFILE_SESSION_KEY = 'ch_profile'
MESSAGE_AUTH_FAILED = 'Auth failed with Companies House'
MESSAGE_NETWORK_ERROR = 'A network error occurred'
COMPANIES_HOUSE_DATE_FORMAT = '%Y-%m-%d'
COMPANY_PROFILE_URL = 'https://api.companieshouse.gov.uk/company/{number}'
COMPANY_OFFICE_URL = (
    'https://api.companieshouse.gov.uk/company/{number}/'
    'registered-office-address'
)


logger = logging.getLogger(__name__)

companies_house_session = requests.Session()


def store_companies_house_profile_in_session(session, company_number):
    response = get_companies_house_profile(number=company_number)
    if not response.ok:
        response.raise_for_status()
    details = response.json()
    session[COMPANIES_HOUSE_PROFILE_SESSION_KEY] = {
        'company_name': details['company_name'],
        'company_status': details['company_status'],
        'date_of_creation': details['date_of_creation'],
    }
    session.modified = True


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


def has_company(sso_user_id):
    response = api_client.supplier.retrieve_profile(
        sso_id=sso_user_id
    )
    if response.ok:
        profile = response.json()
        has_company = bool(profile['company'])
    else:
        has_company = False

    return has_company


def companies_house_client(url):
    auth = requests.auth.HTTPBasicAuth(settings.COMPANIES_HOUSE_API_KEY, '')
    response = companies_house_session.get(url=url, auth=auth)
    if response.status_code == http.client.UNAUTHORIZED:
        logger.error(MESSAGE_AUTH_FAILED)
    return response


def get_companies_house_profile(number):
    url = COMPANY_PROFILE_URL.format(number=number)
    return companies_house_client(url)


def get_companies_house_office_address(number):
    url = COMPANY_OFFICE_URL.format(number=number)
    return companies_house_client(url)


def get_company_date_of_creation_from_session(session):
    return session[COMPANIES_HOUSE_PROFILE_SESSION_KEY]['date_of_creation']


def get_company_name_from_session(session):
    return session[COMPANIES_HOUSE_PROFILE_SESSION_KEY]['company_name']


def get_company_status_from_session(session):
    return session[COMPANIES_HOUSE_PROFILE_SESSION_KEY]['company_status']
