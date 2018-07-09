from directory_components import fields
from directory_components.forms import Form
from directory_validators import enrolment as shared_validators
from directory_validators.company import (
    no_html, no_company_with_insufficient_companies_house_data
)

from django import forms

from enrolment import helpers, validators


class IndentedInvalidFieldsMixin:
    error_css_class = 'input-field-container has-error'


class AutoFocusFieldMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fields = self.visible_fields()
        if fields:
            field = fields[0]
            self.fields[field.name].widget.attrs['autofocus'] = 'autofocus'


class CompanyForm(
    AutoFocusFieldMixin,
    IndentedInvalidFieldsMixin,
    Form
):
    company_name = fields.CharField(
        label='Company name:',
        help_text=(
            "If this is not your company then click back in your browser "
            "and re-enter your company."
        ),
        widget=forms.HiddenInput,
        validators=[no_html],
    )
    company_number = fields.PaddedCharField(
        label='Company number:',
        widget=forms.HiddenInput,
        max_length=8,
        fillchar='0',
    )
    company_address = fields.CharField(
        label='Company registered office address:',
        widget=forms.HiddenInput,
        validators=[no_html],
    )

    confirmed = fields.BooleanField(
        label=(
            'I confirm that I am authorised to sign this '
            'company up to great.gov.uk services'
        )
    )

    def visible_fields(self):
        return []


class CompaniesHouseSearchForm(Form):
    term = fields.CharField()


class CompanyNumberForm(IndentedInvalidFieldsMixin, Form):
    company_number = fields.PaddedCharField(
        validators=helpers.halt_validation_on_failure(
            shared_validators.company_number,
            validators.company_unique,
            validators.company_number_present_and_active,
            no_company_with_insufficient_companies_house_data,
        ),
        max_length=8,
        fillchar='0',
    )


def format_registered_office_address(address):
    fields = [
        'address_line_1',
        'address_line_2',
        'care_of',
        'country',
        'locality',
        'po_box',
        'postal_code',
        'premises',
        'region'
    ]

    return ", ".join(
        address[field] for field in fields if address.get(field)
    )


def get_company_form_initial_data(data):
    """
    Returns the shape of initial data that CompanyForm expects.

    @param {str} name
    @returns dict

    """

    return {
        'company_name': data['company_name'],
        'company_number': data['company_number'],
        'company_address': format_registered_office_address(
            data['registered_office_address']
        )
    }
