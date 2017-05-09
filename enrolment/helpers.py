import http
import logging
import urllib

import requests

from django.conf import settings

from api_client import api_client


COMPANIES_HOUSE_PROFILE_SESSION_KEY = 'ch_profile'
MESSAGE_AUTH_FAILED = 'Auth failed with Companies House'
MESSAGE_NETWORK_ERROR = 'A network error occurred'
COMPANIES_HOUSE_DATE_FORMAT = '%Y-%m-%d'


logger = logging.getLogger(__name__)

companies_house_session = requests.Session()


def store_companies_house_profile_in_session(session, company_number):
    response = CompaniesHouseClient.retrieve_profile(number=company_number)
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


class CompaniesHouseClient:
    api_key = settings.COMPANIES_HOUSE_API_KEY
    base_url = 'https://api.companieshouse.gov.uk'
    endpoints = {
        'profile': 'company/{number}',
        'address': 'company/{number}/registered-office-address',
        'search': 'search/companies',
    }

    @classmethod
    def get_auth(cls):
        return requests.auth.HTTPBasicAuth(cls.api_key, '')

    @classmethod
    def get(cls, url_path, data={}):
        url = urllib.parse.urljoin(cls.base_url, url_path)
        response = companies_house_session.get(
            url=url, data=data, auth=cls.get_auth()
        )
        if response.status_code == http.client.UNAUTHORIZED:
            logger.error(MESSAGE_AUTH_FAILED)
        return response

    @classmethod
    def retrieve_profile(cls, number):
        url = cls.endpoints['profile'].format(number=number)
        return cls.get(url)

    @classmethod
    def retrieve_address(cls, number):
        url = cls.endpoints['address'].format(number=number)
        return cls.get(url)

    @classmethod
    def search(cls, term):
        url = cls.endpoints['search']
        return cls.get(url, {'q': term})


def get_company_date_of_creation_from_session(session):
    return session[COMPANIES_HOUSE_PROFILE_SESSION_KEY]['date_of_creation']


def get_company_name_from_session(session):
    return session[COMPANIES_HOUSE_PROFILE_SESSION_KEY]['company_name']


def get_company_status_from_session(session):
    return session[COMPANIES_HOUSE_PROFILE_SESSION_KEY]['company_status']
