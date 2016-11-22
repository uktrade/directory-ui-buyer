import http
import logging
import datetime

from directory_validators.constants import choices
import requests

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password

from api_client import api_client


EMPLOYEE_CHOICES = {key: value for key, value in choices.EMPLOYEES}
SECTOR_CHOICES = {key: value for key, value in choices.COMPANY_CLASSIFICATIONS}
SMS_CODE_SESSION_KEY = 'sms_code'
COMPANIES_HOUSE_PROFILE_SESSION_KEY = 'ch_profile'
MESSAGE_AUTH_FAILED = 'Auth failed with Companies House'
MESSAGE_NETWORK_ERROR = 'A network error occurred'
COMPANIES_HOUSE_DATE_FORMAT = '%Y-%m-%d'
COMPANY_PROFILE_URL = 'https://api.companieshouse.gov.uk/company/{number}'

logger = logging.getLogger(__name__)

companies_house_session = requests.Session()


def cache_company_details(session, company_number):
    response = get_companies_house_profile(number=company_number)
    if not response.ok:
        response.raise_for_status()
    session[COMPANIES_HOUSE_PROFILE_SESSION_KEY] = response.json()
    session.modified = True


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


def user_has_verified_company(sso_user_id):
    # get from cache
    response = api_client.user.retrieve_profile(
        sso_id=sso_user_id
    )

    if response.ok:
        profile = response.json()
        has_company = bool(
            profile['company'] and
            profile['company_email_confirmed']
        )
    else:
        has_company = False

    return has_company


def get_employees_label(employees_value):
    if not employees_value:
        return employees_value
    return EMPLOYEE_CHOICES.get(employees_value)


def get_sectors_labels(sectors_values):
    if not sectors_values:
        return sectors_values
    return [SECTOR_CHOICES.get(value)for value in sectors_values]


def set_sms_session_code(session, sms_code):
    session[SMS_CODE_SESSION_KEY] = encrypt_sms_code(sms_code)


def encrypt_sms_code(sms_code):
    return make_password(str(sms_code))


def check_encrypted_sms_cookie(provided_sms_code, encoded_sms_code):
    return check_password(
        password=str(provided_sms_code),
        encoded=encoded_sms_code,
    )


def get_sms_session_code(session):
    return session.get(SMS_CODE_SESSION_KEY, '')


def companies_house_client(url):
    auth = requests.auth.HTTPBasicAuth(settings.COMPANIES_HOUSE_API_KEY, '')
    response = companies_house_session.get(url=url, auth=auth)
    if response.status_code == http.client.UNAUTHORIZED:
        logger.error(MESSAGE_AUTH_FAILED)
    return response


def get_companies_house_profile(number):
    url = COMPANY_PROFILE_URL.format(number=number)
    return companies_house_client(url)


def get_cached_company_date_of_creation(session):
    return session[COMPANIES_HOUSE_PROFILE_SESSION_KEY]['date_of_creation']


def get_cached_company_name(session):
    return session[COMPANIES_HOUSE_PROFILE_SESSION_KEY]['company_name']


def get_cached_company_status(session):
    return session[COMPANIES_HOUSE_PROFILE_SESSION_KEY]['company_status']


def format_date_of_creation(raw_date_of_creation):
    if not raw_date_of_creation:
        return raw_date_of_creation
    date_of_creation = datetime.datetime.strptime(
        raw_date_of_creation,
        '%Y-%m-%d'
    )
    return date_of_creation.strftime('%d %b %Y')


def inflate_company_profile_from_response(response):
    details = response.json()
    date_of_creation = format_date_of_creation(details.get('date_of_creation'))
    return {
        'website': details['website'],
        'description': details['description'],
        'number': details['number'],
        'date_of_creation': date_of_creation,
        'sectors': get_sectors_labels(details['sectors']),
        'logo': details['logo'],
        'name': details['name'],
        'keywords': details['keywords'],
        'employees': get_employees_label(details['employees']),
    }
