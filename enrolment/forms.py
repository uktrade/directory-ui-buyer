from django import forms
from django.utils.safestring import mark_safe

from directory_validators import enrolment as shared_validators
from directory_validators.company import no_html
from directory_constants.constants import urls

from enrolment import fields, helpers, validators
from enrolment.widgets import CheckboxWithInlineLabel


class IndentedInvalidFieldsMixin:
    error_css_class = 'input-field-container has-error'


class AutoFocusFieldMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        first_field = self.visible_fields()[0]
        self.fields[first_field.name].widget.attrs['autofocus'] = 'autofocus'


class CompanyForm(
    AutoFocusFieldMixin,
    IndentedInvalidFieldsMixin,
    forms.Form
):
    company_name = forms.CharField(
        label='Company name:',
        help_text=(
            "If this is not your company then click back in your browser "
            "and re-enter your company."
        ),
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
        validators=[no_html],
    )
    company_number = fields.PaddedCharField(
        label='Company number:',
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
        max_length=8,
        fillchar='0',
    )
    company_address = forms.CharField(
        label='Company registered office address:',
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
        validators=[no_html],
    )


class CompanyExportStatusForm(
    AutoFocusFieldMixin, IndentedInvalidFieldsMixin, forms.Form
):
    has_exported_before = forms.TypedChoiceField(
        label=(
            'Have you exported before?'
        ),
        coerce=lambda x: x == 'True',
        choices=[(True, 'Yes'), (False, 'No')],
        widget=forms.RadioSelect()
    )
    terms_agreed = forms.BooleanField(
        label='',
        widget=CheckboxWithInlineLabel(
            label=mark_safe(
                'I accept the '
                '<a href="{url}" target="_blank">Find a Buyer terms and '
                'conditions</a>'.format(
                    url=urls.TERMS_AND_CONDITIONS_URL)
            ),
        ),
    )


class CompaniesHouseSearchForm(forms.Form):
    term = forms.CharField()


class CompanyNumberForm(IndentedInvalidFieldsMixin, forms.Form):
    company_number = fields.PaddedCharField(
        validators=helpers.halt_validation_on_failure(
            shared_validators.company_number,
            validators.company_unique,
            validators.company_number_present_and_active,
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
