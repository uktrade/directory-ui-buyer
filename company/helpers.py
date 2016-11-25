import datetime

from directory_validators.constants import choices


EMPLOYEE_CHOICES = {key: value for key, value in choices.EMPLOYEES}
SECTOR_CHOICES = {key: value for key, value in choices.COMPANY_CLASSIFICATIONS}


def format_date_of_creation(raw_date_of_creation):
    if not raw_date_of_creation:
        return raw_date_of_creation
    date_of_creation = datetime.datetime.strptime(
        raw_date_of_creation,
        '%Y-%m-%d'
    )
    return date_of_creation.strftime('%d %b %Y')


def get_employees_label(employees_value):
    if not employees_value:
        return employees_value
    return EMPLOYEE_CHOICES.get(employees_value)


def get_sectors_labels(sectors_values):
    if not sectors_values:
        return sectors_values
    return [SECTOR_CHOICES.get(value) for value in sectors_values]


def get_public_company_profile_from_response(response):
    return format_company_details(response.json())


def get_company_profile_from_response(response):
    return format_company_details(response.json())


def get_company_list_from_response(response):
    parsed = response.json()
    if parsed['results']:
        parsed['results'] = map(format_company_details, parsed['results'])
    return parsed


def format_company_details(details):
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
        'supplier_case_studies': details['supplier_case_studies']
    }
