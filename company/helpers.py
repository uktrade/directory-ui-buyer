import datetime

from directory_validators.constants import choices
from directory_validators.helpers import tokenize_keywords

from django.conf import settings

from api_client import api_client
from enrolment.helpers import CompaniesHouseClient


EMPLOYEE_CHOICES = {key: value for key, value in choices.EMPLOYEES}
SECTOR_CHOICES = {key: value for key, value in choices.COMPANY_CLASSIFICATIONS}


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
        'website': details['website'],
        'description': details['description'],
        'summary': details['summary'],
        'number': details['number'],
        'date_of_creation': date_of_creation,
        'sectors': pair_sector_values_with_label(details['sectors']),
        'logo': details['logo'],
        'name': details['name'],
        'keywords': tokenize_keywords(keywords) if keywords else [],
        'employees': get_employees_label(details['employees']),
        'supplier_case_studies': list(case_studies),
        'modified': format_date_modified(details['modified']),
        'verified_with_code': details['verified_with_code'],
        'postal_full_name': details['postal_full_name'],
        'address_line_1': details['address_line_1'],
        'address_line_2': details['address_line_2'],
        'locality': details['locality'],
        'country': details['country'],
        'postal_code': details['postal_code'],
        'po_box': details['po_box'],
        'mobile_number': details['mobile_number'],
        'twitter_url': details['twitter_url'],
        'facebook_url': details['facebook_url'],
        'linkedin_url': details['linkedin_url'],
        'email_address': details['email_address'],
        'email_full_name': details['email_full_name'],
        'has_valid_address': details['has_valid_address'],
        'twitter_url': details['twitter_url'],
        'facebook_url': details['facebook_url'],
        'linkedin_url': details['linkedin_url'],
        'is_published': details['is_published'],
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


def get_company_profile(sso_id):
    response = api_client.company.retrieve_private_profile(sso_id)
    if not response.ok:
        response.raise_for_status()
    return response.json()


def get_company_contact_details_from_companies_house(number):
    response = CompaniesHouseClient.retrieve_address(number)
    if not response.ok:
        response.raise_for_status()
    return response.json()


def get_contact_details(sso_id):
    profile = get_company_profile(sso_id)
    if profile['has_valid_address']:
        return profile
    return get_company_contact_details_from_companies_house(profile['number'])


def chunk_list(unchunked, length):
    return [unchunked[x:x+length] for x in range(0, len(unchunked), length)]
