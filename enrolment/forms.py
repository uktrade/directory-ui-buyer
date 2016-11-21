
from directory_validators import enrolment as shared_enrolment_validators
from directory_validators import company as shared_company_validators
from directory_validators.constants import choices

from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe

from enrolment import fields, helpers, validators


class IndentedInvalidFieldsMixin:
    error_css_class = 'input-field-container has-error'


class AutoFocusFieldMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        first_field_name = next(field for field in self.fields)
        self.fields[first_field_name].widget.attrs['autofocus'] = 'autofocus'


class CompanyForm(AutoFocusFieldMixin, IndentedInvalidFieldsMixin, forms.Form):
    company_number = fields.PaddedCharField(
        label='Company number:',
        help_text=mark_safe(
            'This is the company number on your certificate of '
            'incorporation. Find your company number from '
            '<a href="{url}" target="_blank">Companies House'
            '</a>.'.format(url=settings.COMPANIES_HOUSE_SEARCH_URL)
        ),
        validators=helpers.halt_validation_on_failure(
            shared_enrolment_validators.company_number,
            validators.company_number,
        ),
        max_length=8,
        fillchar='0',
    )


class CompanyNameForm(AutoFocusFieldMixin, IndentedInvalidFieldsMixin,
                      forms.Form):
    name = forms.CharField(
        label='Company name:',
        help_text=(
            "If this is not your company then click back in your browser "
            "and re-enter your company's number."
        ),
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
    )


class CompanyExportStatusForm(AutoFocusFieldMixin, IndentedInvalidFieldsMixin,
                              forms.Form):
    export_status = forms.ChoiceField(
        label=(
            'Has your company sold products or services to overseas customers?'
        ),
        choices=choices.EXPORT_STATUSES,
        validators=[shared_enrolment_validators.export_status_intention]
    )


class CompanyBasicInfoForm(AutoFocusFieldMixin, IndentedInvalidFieldsMixin,
                           forms.Form):
    name = forms.CharField(
        label='Change your company name',
        help_text=(
            'Enter your preferred business name'
        ),
        max_length=255,
    )
    website = forms.URLField(
        max_length=255,
        help_text=(
            'The website address must start with either http:// or '
            'https://'
        )
    )
    keywords = forms.CharField(
        label=(
            'Enter up to 10 keywords that describe your company '
            '(separated by commas):'
        ),
        help_text=(
            'These keywords will be used to help potential overseas buyers '
            'find your company.'
        ),
        widget=forms.Textarea,
        max_length=1000,
        validators=[shared_company_validators.keywords_word_limit]
    )


class CompanyDescriptionForm(AutoFocusFieldMixin, IndentedInvalidFieldsMixin,
                             forms.Form):
    description = forms.CharField(
        widget=forms.Textarea,
        label='Describe your business to overseas buyers:',
        help_text='Maximum 1,000 characters.',
        max_length=1000,
    )


class CompanyLogoForm(AutoFocusFieldMixin, IndentedInvalidFieldsMixin,
                      forms.Form):
    logo = forms.FileField(
        help_text=(
            'For best results this should be a transparent PNG file of 600 x '
            '600 pixels and no more than {0}MB'.format(
                int(settings.VALIDATOR_MAX_LOGO_SIZE_BYTES / 1024 / 1014)
            )
        ),
        required=True,
        validators=[shared_enrolment_validators.logo_filesize]
    )


class CompanyEmailAddressForm(AutoFocusFieldMixin, IndentedInvalidFieldsMixin,
                              forms.Form):
    error_messages = {
        'different': 'Your emails do not match.'
    }
    company_email = forms.EmailField(
        label='Email address:',
        help_text=(
            'Please enter a company email address rather than a personal '
            'email address.'
        ),
        validators=helpers.halt_validation_on_failure(
            shared_enrolment_validators.email_domain_free,
            shared_enrolment_validators.email_domain_disposable,
            validators.email_address,
        )
    )
    email_confirmed = forms.EmailField(
        label='Please confirm your email address:',
    )

    def clean_email_confirmed(self):
        email = self.cleaned_data.get('company_email')
        confirmed = self.cleaned_data.get('email_confirmed')
        if (email and confirmed and email != confirmed):
            raise forms.ValidationError(self.error_messages['different'])
        return confirmed


class UserForm(AutoFocusFieldMixin, IndentedInvalidFieldsMixin, forms.Form):
    error_messages = {
        'different': 'Your phone numbers do not match.'
    }
    mobile_number = fields.MobilePhoneNumberField(
        label='Your mobile phone number:',
        help_text=(
            'We will send a verification code to this mobile phone number.'
        ),
        validators=helpers.halt_validation_on_failure(
            validators.mobile_number,
        )
    )
    mobile_confirmed = forms.CharField(
        label='Please confirm your mobile phone number:'
    )
    terms_agreed = forms.BooleanField(
        label=mark_safe(
            'Tick this box to accept the '
            '<a href="/terms_and_conditions" target="_blank">terms and '
            'conditions</a> of the Find a Buyer service.'
        )
    )
    referrer = forms.CharField(required=False, widget=forms.HiddenInput())

    def clean_mobile_confirmed(self):
        mobile = self.cleaned_data.get('mobile_number')
        confirmed = self.cleaned_data.get('mobile_confirmed')
        if (mobile and confirmed and mobile != confirmed):
            raise forms.ValidationError(self.error_messages['different'])
        return confirmed


class CompanySizeForm(AutoFocusFieldMixin, IndentedInvalidFieldsMixin,
                      forms.Form):
    employees = forms.ChoiceField(
        choices=choices.EMPLOYEES,
        label='How many employees are in your company?',
        help_text=(
            'Tell international buyers more about your business to ensure '
            'the right buyers can find you.'
        )
    )


class CompanyClassificationForm(AutoFocusFieldMixin,
                                IndentedInvalidFieldsMixin, forms.Form):
    sectors = forms.MultipleChoiceField(
        label=(
            'What sectors is your company interested in working in? '
            'Choose no more than 10 sectors.'
        ),
        choices=choices.COMPANY_CLASSIFICATIONS,
        widget=forms.CheckboxSelectMultiple(),
        validators=[shared_company_validators.sector_choice_limit]
    )


class PhoneNumberVerificationForm(AutoFocusFieldMixin,
                                  IndentedInvalidFieldsMixin, forms.Form):

    error_messages = {
        'different': 'Incorrect code.'
    }

    sms_code = forms.CharField(
        label='Enter the verification code from the text message we sent you:',
        help_text=mark_safe(
            'We sent you a text message containing a six digit code. Continue '
            'creating your Find a Buyer profile by entering this code. '
            '<a href="/register/mobile" target="_self">'
            'Create a new code</a> if you do not receive the text message in '
            '10 minutes.'
        ),
    )

    def __init__(self, *args, **kwargs):
        self.expected_sms_code = kwargs.pop('expected_sms_code')
        super().__init__(*args, **kwargs)

    def clean_sms_code(self):
        sms_code = self.cleaned_data['sms_code']
        if sms_code != self.expected_sms_code:
            raise forms.ValidationError(self.error_messages['different'])
        return sms_code


class InternationalBuyerForm(AutoFocusFieldMixin, IndentedInvalidFieldsMixin,
                             forms.Form):
    PLEASE_SELECT_LABEL = 'Please select a sector'
    TERMS_CONDITIONS_MESSAGE = ('Tick the box to confirm you agree to '
                                'the terms and conditions.')

    full_name = forms.CharField(label='Your name')
    email_address = forms.EmailField(label='Your email address')
    sector = forms.ChoiceField(
        label='Sector',
        choices=(
            [['', PLEASE_SELECT_LABEL]] + list(choices.COMPANY_CLASSIFICATIONS)
        )
    )
    terms = forms.BooleanField(
        label=mark_safe(
            'I agree to the <a target="_self" '
            'href="/terms_and_conditions">terms and conditions</a> of '
            'Exporting is GREAT.'
        ),
        error_messages={'required': TERMS_CONDITIONS_MESSAGE}
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
        'company_name': cleaned_data['name'],
        'company_number': cleaned_data['company_number'],
        'mobile_number': cleaned_data['mobile_number'],
        'referrer': cleaned_data['referrer'],
        'export_status': cleaned_data['export_status'],
    }


def serialize_company_profile_forms(cleaned_data):
    """
    Return the shape directory-api-client expects for company profile edit.

    @param {dict} cleaned_data - All the fields in `CompanyBasicInfoForm`
                                 `CompanySizeForm`, `CompanyLogoForm`, and
                                 `CompanyClassificationForm`
    @returns dict

    """

    return {
        'name': cleaned_data['name'],
        'website': cleaned_data['website'],
        'keywords': cleaned_data['keywords'],
        'employees': cleaned_data['employees'],
        'sectors': cleaned_data['sectors'],
    }


def serialize_company_logo_forms(cleaned_data):
    """
    Return the shape directory-api-client expects for changing logo.

    @param {dict} cleaned_data - All the fields in `CompanyLogoForm`
    @returns dict

    """

    return {
        'logo': cleaned_data['logo'],
    }


def serialize_company_description_forms(cleaned_data):
    """
    Return the shape directory-api-client expects for changing description.

    @param {dict} cleaned_data - All the fields in `CompanyDescriptionForm`
    @returns dict

    """

    return {
        'description': cleaned_data['description'],
    }


def serialize_international_buyer_forms(cleaned_data):
    """
    Return the shape directory-api-client expects for saving international
    buyers.

    @param {dict} cleaned_data - All the fields in `InternationalBuyerForm`
    @returns dict

    """

    return {
        'name': cleaned_data['full_name'],
        'email': cleaned_data['email_address'],
        'sector': cleaned_data['sector'],
    }


def get_company_name_form_initial_data(name):
    """
    Returns the shape of initial data that CompanyNameForm expects.

    @param {str} name
    @returns dict

    """

    return {
        'name': name,
    }


def get_user_form_initial_data(referrer):
    """
    Returns the shape of initial data that UserForm expects.

    @param {str} referrer
    @returns dict

    """

    return {
        'referrer': referrer,
    }


def get_email_form_initial_data(email):
    """
    Returns the shape of initial data that CompanyEmailAddressForm expects.

    @param {str} email
    @returns dict

    """

    return {
        'company_email': email,
        'email_confirmed': email,
    }
