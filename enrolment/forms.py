from django import forms
from django.conf import settings

from directory_validators import enrolment as shared_validators

from enrolment import constants, helpers, validators


class CompanyForm(forms.Form):
    company_number = forms.CharField(
        label='Company number',
        help_text=('This is the 8-digit number on the company certificate of '
                   'incorporation.'),
        validators=helpers.halt_validation_on_failure(
            shared_validators.company_number,
            validators.company_number,
        )
    )


class CompanyNameForm(forms.Form):
    company_name = forms.CharField(
        label='Company Name'
    )


class CompanyBasicInfoForm(forms.Form):
    # TODO: ED-145
    # Make sure all fields have char limits once the models are defined
    company_name = forms.CharField()
    website = forms.URLField()
    description = forms.CharField(widget=forms.Textarea)
    logo = forms.FileField(
        help_text=(
            'Maximum filesize: {0}MB'.format(
                settings.VALIDATOR_MAX_LOGO_SIZE_BYTES / 1024 / 1014
            )
        ),
        required=False,
        validators=[shared_validators.logo_filesize]
    )


class AimsForm(forms.Form):
    aim_one = forms.ChoiceField(choices=constants.AIMS)
    aim_two = forms.ChoiceField(choices=constants.AIMS)


class UserForm(forms.Form):
    name = forms.CharField(label='Full name')
    email = forms.EmailField(
        label='Email address',
        validators=[
            shared_validators.email_domain_free,
            shared_validators.email_domain_disposable,
        ]
    )
    password = forms.CharField(widget=forms.PasswordInput())
    terms_agreed = forms.BooleanField()
    referrer = forms.CharField(required=False, widget=forms.HiddenInput())


class CompanySizeForm(forms.Form):
    turnover = forms.CharField(
        label='Company turnover (GBP)',
        required=False,
        help_text='What is the correct turnover for your company?'
    )
    employees = forms.ChoiceField(
        choices=constants.EMPLOYEES,
        help_text='How many employees are in your company?'
    )


class CompanyClassificationForm(forms.Form):
    sectors = forms.MultipleChoiceField(
        label='What sectors is your company interested in working in?',
        choices=constants.COMPANY_CLASSIFICATIONS,
        widget=forms.CheckboxSelectMultiple()
    )


def serialize_enrolment_forms(cleaned_data):
    """
    Return the shape directory-api-client expects for enrolment.

    @param {dict} cleaned_data - All the fields in `CompanyForm`, `AimsForm`,
                                 `AimsForm`, and `CompanyNameForm`
    @returns dict

    """

    return {
        'aims': [cleaned_data['aim_one'], cleaned_data['aim_two']],
        'company_name': cleaned_data['company_name'],
        'company_number': cleaned_data['company_number'],
        'email': cleaned_data['email'],
        'password': cleaned_data['password'],
        'personal_name': cleaned_data['name'],
        'referrer': cleaned_data['referrer'],
    }


def serialize_company_profile_forms(cleaned_data):
    """
    Return the shape directory-api-client expects for enrolment.

    @param {dict} cleaned_data - All the fields in `CompanyBasicInfoForm`
                                 and `CompanySizeForm`, and
                                 `CompanyClassificationForm`
    @returns dict

    """

    return {
        'name': cleaned_data['company_name'],
        'website': cleaned_data['website'],
        'description': cleaned_data['description'],
        'logo': cleaned_data['logo'],
        'turnover': cleaned_data['turnover'],
        'employees': cleaned_data['employees'],
        'sectors': cleaned_data['sectors'],
    }
