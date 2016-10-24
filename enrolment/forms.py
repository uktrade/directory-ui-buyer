from django import forms
from django.conf import settings

from directory_validators import enrolment as shared_validators
from directory_validators.constants import choices

from enrolment import helpers, validators


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


class CompanyExportStatusForm(forms.Form):
    export_status = forms.ChoiceField(
        label=(
            'Has your company sold products or services to overseas customers?'
        ),
        choices=choices.EXPORT_STATUSES,
        validators=[shared_validators.export_status_intention]
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


class CompanyEmailAddressForm(forms.Form):
    company_email = forms.EmailField(
        label='Email',
        help_text='Your company email address',
        validators=[
            shared_validators.email_domain_free,
            shared_validators.email_domain_disposable,
        ]
    )
    email_confirmed = forms.EmailField(
        label='Email confirmed',
        help_text='Confirm your email address',
    )

    def clean_email_confirmed(self):
        email = self.cleaned_data.get('company_email')
        confirmed = self.cleaned_data.get('email_confirmed')
        if (email and confirmed and email != confirmed):
            raise forms.ValidationError('Your emails do not match')
        return confirmed


class UserForm(forms.Form):
    mobile_number = forms.CharField(
        label='Mobile number'
    )
    mobile_confirmed = forms.CharField(
        label='Mobile number confirmed'
    )
    terms_agreed = forms.BooleanField()
    referrer = forms.CharField(required=False, widget=forms.HiddenInput())

    def clean_mobile_confirmed(self):
        mobile = self.cleaned_data.get('mobile_number')
        confirmed = self.cleaned_data.get('mobile_confirmed')
        if (mobile and confirmed and mobile != confirmed):
            raise forms.ValidationError('Your numbers do not match')
        return confirmed


class CompanySizeForm(forms.Form):
    turnover = forms.CharField(
        label='Company turnover (GBP)',
        required=False,
        help_text='What is the correct turnover for your company?'
    )
    employees = forms.ChoiceField(
        choices=choices.EMPLOYEES,
        help_text='How many employees are in your company?'
    )


class CompanyClassificationForm(forms.Form):
    sectors = forms.MultipleChoiceField(
        label='What sectors is your company interested in working in?',
        choices=choices.COMPANY_CLASSIFICATIONS,
        widget=forms.CheckboxSelectMultiple()
    )


def serialize_enrolment_forms(cleaned_data):
    """
    Return the shape directory-api-client expects for enrolment.

    @param {dict} cleaned_data - All the fields in `CompanyForm`, `UserForm`,
                                 `CorporateEmailAddressForm`,
                                 `CompanyNameForm`, and
                                 `CompanyExportStatusForm`
    @returns dict

    """

    return {
        'company_email': cleaned_data['company_email'],
        'company_name': cleaned_data['company_name'],
        'company_number': cleaned_data['company_number'],
        'mobile_number': cleaned_data['mobile_number'],
        'referrer': cleaned_data['referrer'],
        'export_status': cleaned_data['export_status'],
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
