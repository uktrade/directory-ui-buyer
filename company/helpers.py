from directory_api_client.client import api_client


def get_company_profile(sso_session_id):
    response = api_client.company.retrieve_private_profile(
        sso_session_id=sso_session_id
    )
    response.raise_for_status()
    return response.json()


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
