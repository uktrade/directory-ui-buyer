import datetime

from directory_constants.constants import choices
from directory_validators.helpers import tokenize_keywords

from django.conf import settings

from api_client import api_client


EMPLOYEE_CHOICES = {key: value for key, value in choices.EMPLOYEES}
SECTOR_CHOICES = {key: value for key, value in choices.INDUSTRIES}


def format_date_of_creation(raw_date):
    if not raw_date:
        return raw_date
    return datetime.datetime.strptime(raw_date, '%Y-%m-%d')


def format_date_modified(raw_date):
    if not raw_date:
        return raw_date
    return datetime.datetime.strptime(raw_date, '%Y-%m-%dT%H:%M:%S.%fZ')


def get_employees_label(employees_value):
    if not employees_value:
        return employees_value
    return EMPLOYEE_CHOICES.get(employees_value)


def pair_sector_values_with_label(sectors_values):
    if not sectors_values:
        return []
    return [pair_sector_value_with_label(value) for value in sectors_values]


def pair_sector_value_with_label(sectors_value):
    return {'value': sectors_value, 'label': get_sectors_label(sectors_value)}


def get_sectors_label(sectors_value):
    if not sectors_value:
        return sectors_value
    return SECTOR_CHOICES.get(sectors_value)


def get_public_company_profile_from_response(response):
    return format_company_details(response.json())


def get_company_profile_from_response(response):
    return format_company_details(response.json())


def get_company_list_from_response(response):
    parsed = response.json()
    if parsed['results']:
        results = map(format_company_details, parsed['results'])
        parsed['results'] = list(results)
    return parsed


def format_company_details(details):
    date_of_creation = format_date_of_creation(details.get('date_of_creation'))
    case_studies = map(format_case_study, details['supplier_case_studies'])
    keywords = details['keywords']
    return {
        **details,
        'date_of_creation': date_of_creation,
        'sectors': pair_sector_values_with_label(details['sectors']),
        'keywords': tokenize_keywords(keywords) if keywords else [],
        'employees': get_employees_label(details['employees']),
        'supplier_case_studies': list(case_studies),
        'modified': format_date_modified(details['modified']),
        'public_profile_url': get_public_profile_url(details['number'])
    }


def format_case_study(case_study):
    sector_value = case_study['sector']
    case_study['sector'] = {
        'url': settings.SUPPLIER_PROFILE_LIST_URL.format(sectors=sector_value),
        'label': get_sectors_label(sector_value),
    }
    case_study['url'] = get_case_study_url(case_study['pk'])
    return case_study


def get_case_study_url(case_study_id):
    return settings.SUPPLIER_CASE_STUDY_URL.format(id=case_study_id)


def get_public_profile_url(company_number):
    return settings.SUPPLIER_PROFILE_URL.format(number=company_number)


def get_company_profile(sso_session_id):
    response = api_client.company.retrieve_private_profile(
        sso_session_id=sso_session_id
    )
    response.raise_for_status()
    return response.json()


def chunk_list(unchunked, length):
    return [unchunked[x:x+length] for x in range(0, len(unchunked), length)]


def build_company_address(company_profile):
    field_names = [
        'address_line_1',
        'address_line_2',
        'locality',
        'country',
        'postal_code',
        'po_box',
    ]
    address_parts = []
    for field_name in field_names:
        value = company_profile.get(field_name)
        if value:
            address_parts.append(value)
    return ', '.join(address_parts)
