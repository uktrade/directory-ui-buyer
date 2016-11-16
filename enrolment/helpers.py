from directory_api_client.client import DirectoryAPIClient
from directory_validators.constants import choices

from django.conf import settings

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
    response = api_client.company.retrieve_companies_house_profile(number)
    if not response.ok:
        response.raise_for_status()
    return response.json()['company_name']


def user_has_verified_company(sso_user_id):
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
