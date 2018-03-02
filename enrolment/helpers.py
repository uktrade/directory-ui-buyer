from collections import OrderedDict
from functools import partial
import http
import logging
import urllib
from urllib.parse import urljoin

from django.conf import settings
from django.forms import ValidationError
from django.shortcuts import render

import requests
from requests.exceptions import RequestException

from api_client import api_client
from enrolment import validators


COMPANIES_HOUSE_PROFILE_SESSION_KEY = 'ch_profile'
MESSAGE_AUTH_FAILED = 'Auth failed with Companies House'
MESSAGE_NETWORK_ERROR = 'A network error occurred'
COMPANIES_HOUSE_DATE_FORMAT = '%Y-%m-%d'


logger = logging.getLogger(__name__)


def get_company_from_companies_house(company_number):
    response = CompaniesHouseClient.retrieve_profile(number=company_number)
    response.raise_for_status()
    return response.json()


def store_companies_house_profile_in_session(session, company_number):
    details = get_company_from_companies_house(company_number)
    session[COMPANIES_HOUSE_PROFILE_SESSION_KEY] = {
        'company_name': details['company_name'],
        'company_status': details['company_status'],
        'date_of_creation': details.get('date_of_creation'),
        'company_number': company_number,
        'registered_office_address': details['registered_office_address']
    }
    session.modified = True


def halt_validation_on_failure(*all_validators):
    """
    Django runs all validators on a field and shows all errors. Sometimes this
    is undesirable: we may want the validators to stop on the first error.

    """
    def inner(value):
        for validator in all_validators:
            validator(value)
    inner.inner_validators = all_validators
    return [inner]


def has_company(sso_session_id):
    response = api_client.supplier.retrieve_profile(
        sso_session_id=sso_session_id
    )
    if response.ok:
        profile = response.json()
        has_company = bool(profile['company'])
    else:
        has_company = False

    return has_company


class CompaniesHouseClient:
    api_key = settings.COMPANIES_HOUSE_API_KEY
    client_id = settings.COMPANIES_HOUSE_CLIENT_ID
    client_secret = settings.COMPANIES_HOUSE_CLIENT_SECRET
    make_api_url = partial(urljoin, 'https://api.companieshouse.gov.uk')
    make_oauth2_url = partial(urljoin, 'https://account.companieshouse.gov.uk')
    endpoints = {
        'profile': make_api_url('company/{number}'),
        'address': make_api_url('company/{number}/registered-office-address'),
        'search': make_api_url('search/companies'),
        'oauth2': make_oauth2_url('oauth2/authorise'),
        'oauth2-token': make_oauth2_url('oauth2/token'),
    }
    session = requests.Session()

    @classmethod
    def get_auth(cls):
        return requests.auth.HTTPBasicAuth(cls.api_key, '')

    @classmethod
    def get(cls, url, params={}):
        response = cls.session.get(url=url, params=params, auth=cls.get_auth())
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
        return cls.get(url, params={'q': term})

    @classmethod
    def make_oauth2_url(cls, redirect_uri, company_number):
        # ordered dict to facilitate testing
        params = OrderedDict([
            ('client_id', cls.client_id),
            ('redirect_uri', redirect_uri),
            ('response_type', 'code'),
            ('scope', cls.endpoints['profile'].format(number=company_number)),
        ])
        return cls.endpoints['oauth2'] + '?' + urllib.parse.urlencode(params)

    @classmethod
    def verify_oauth2_code(cls, code, redirect_uri):
        url = cls.endpoints['oauth2-token']
        params = OrderedDict([
            ('grant_type', 'authorization_code'),
            ('code', code),
            ('client_id', cls.client_id),
            ('client_secret', cls.client_secret),
            ('redirect_uri', redirect_uri),
        ])
        return cls.session.post(url=url + '?' + urllib.parse.urlencode(params))


def get_date_of_creation_from_session(session):
    return session[
        COMPANIES_HOUSE_PROFILE_SESSION_KEY
    ]['date_of_creation']


def get_company_number_from_session(session):
    key = 'company_number'
    return session.get(COMPANIES_HOUSE_PROFILE_SESSION_KEY, {}).get(key)


def get_company_name_from_session(session):
    return get_company_from_session(session)['company_name']


def get_company_status_from_session(session):
    return get_company_from_session(session)['company_status']


def get_company_address_from_session(session):
    return get_company_from_session(session)['registered_office_address']


def get_company_from_session(session):
    return session.get(COMPANIES_HOUSE_PROFILE_SESSION_KEY, {})


def store_companies_house_profile_in_session_and_validate(
        session, company_number
):
    try:
        store_companies_house_profile_in_session(
            session=session,
            company_number=company_number,
        )
    except RequestException as error:
        error = getattr(error, 'response', None)
        status_code = getattr(error, 'status_code', None)
        if status_code == http.client.NOT_FOUND:
            raise ValidationError(validators.MESSAGE_COMPANY_NOT_FOUND)
        else:
            raise ValidationError(validators.MESSAGE_COMPANY_ERROR)
    else:
        company_status = get_company_status_from_session(
            session
        )
        validators.company_active(company_status)
        validators.company_unique(company_number)


def get_error_response(request, context):
    return render(request, 'enrolment-error.html', context)
