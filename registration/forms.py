from django import forms

from directory_validators import enrolment as validators
from directory_validators.constants import MAX_LOGO_SIZE_MEGABYTES

from registration import constants


class CompanyForm(forms.Form):
    company_number = forms.CharField(
        label='Company number',
        help_text=('This is the 8-digit number on the company certificate of '
                   'incorporation.'),
        validators=[validators.company_number]
    )


class CompanyBasicInfoForm(forms.Form):
    # TODO: ED-145
    # Make sure all fields have char limits once the models are defined
    company_name = forms.CharField()
    website = forms.URLField()
    description = forms.CharField(widget=forms.Textarea)
    logo = forms.FileField(
        help_text=(
            'Maximum filesize: {0}MB'.format(MAX_LOGO_SIZE_MEGABYTES)
        ),
        required=False,
        validators=[validators.logo_filesize]
    )


class AimsForm(forms.Form):
    aim_one = forms.ChoiceField(choices=constants.AIMS)
    aim_two = forms.ChoiceField(choices=constants.AIMS)


class UserForm(forms.Form):
    name = forms.CharField(label='Full name')
    email = forms.EmailField(
        label='Email address',
        validators=[
            validators.email_domain_free,
            validators.email_domain_disposable,
        ]
    )
    password = forms.CharField(widget=forms.PasswordInput())
    terms_agreed = forms.BooleanField()
    referrer = forms.CharField(required=False, widget=forms.HiddenInput())


def serialize_registration_forms(cleaned_data):
    """
    Return the shape directory-api-client expects for registration.

    @param {dict} cleaned_data - All the fields in `CompanyForm`,
                                `AimsForm`, and `AimsForm`.
    @returns dict

    """

    return {
        'aims': [cleaned_data['aim_one'], cleaned_data['aim_two']],
        'company_number': cleaned_data['company_number'],
        'email': cleaned_data['email'],
        'personal_name': cleaned_data['name'],
        'password': cleaned_data['password'],
        'referrer': cleaned_data['referrer'],
    }


def serialize_company_profile_forms(cleaned_data):
    """
    Return the shape directory-api-client expects for registration.

    @param {dict} cleaned_data - All the fields in `CompanyBasicInfoForm`
    @returns dict

    """

    return {
        'name': cleaned_data['company_name'],
        'website': cleaned_data['website'],
        'description': cleaned_data['description'],
        'logo': cleaned_data['logo']
    }
