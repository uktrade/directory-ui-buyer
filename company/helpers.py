import datetime

from directory_validators.constants import choices

from api_client import api_client

from enrolment.helpers import get_companies_house_office_address


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


def get_case_study_details_from_response(response):
    parsed = response.json()
    # `format_company_details` expects `supplier_case_studies` key.
    parsed['company']['supplier_case_studies'] = []
    parsed['sector'] = pair_sector_value_with_label(parsed['sector'])
    parsed['company'] = format_company_details(parsed['company'])
    return parsed


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
    # If the contact details json is set to null
    # then details['contact_details'] will be None
    contact_details = details['contact_details'] or {}
    case_studies = map(format_case_study, details['supplier_case_studies'])
    return {
        'website': details['website'],
        'description': details['description'],
        'number': details['number'],
        'date_of_creation': date_of_creation,
        'sectors': pair_sector_values_with_label(details['sectors']),
        'logo': details['logo'],
        'name': details['name'],
        'keywords': details['keywords'],
        'employees': get_employees_label(details['employees']),
        'supplier_case_studies': list(case_studies),
        'modified': format_date_modified(details['modified']),
        'verified_with_code': details['verified_with_code'],
        'is_address_set': contact_details != {},
        'contact_details': contact_details,
    }


def format_case_study(case_study):
    case_study['sector'] = pair_sector_value_with_label(case_study['sector'])
    return case_study


def get_company_profile(sso_id):
    response = api_client.company.retrieve_profile(sso_id)
    if not response.ok:
        response.raise_for_status()
    return response.json()


def get_company_contact_details_from_companies_house(number):
    response = get_companies_house_office_address(number)
    if not response.ok:
        response.raise_for_status()
    return response.json()


def get_contact_details(sso_id):
    profile = get_company_profile(sso_id)
    is_address_known = (
        profile.get('contact_details') and
        profile['contact_details'].get('address_line_1')
    )
    if is_address_known:
        return profile['contact_details']
    return get_company_contact_details_from_companies_house(profile['number'])
