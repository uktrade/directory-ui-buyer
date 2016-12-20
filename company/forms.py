from directory_validators import company as shared_validators
from directory_validators import enrolment as shared_enrolment_validators
from directory_validators.constants import choices

from django import forms
from django.conf import settings
from django.core.signing import Signer
from django.utils.safestring import mark_safe

from company import validators
from enrolment.forms import IndentedInvalidFieldsMixin, AutoFocusFieldMixin
from enrolment.helpers import halt_validation_on_failure


class PublicProfileSearchForm(IndentedInvalidFieldsMixin, AutoFocusFieldMixin,
                              forms.Form):
    sectors = forms.ChoiceField(
        choices=choices.COMPANY_CLASSIFICATIONS,
    )
    page = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput,
        initial=1,
    )

    def clean_page(self):
        return self.cleaned_data['page'] or self.fields['page'].initial


class CaseStudyBasicInfoForm(IndentedInvalidFieldsMixin, AutoFocusFieldMixin,
                             forms.Form):
    title = forms.CharField(
        label='Title of your case study of project:',
        help_text='Give your case study a title of 60 characters or fewer.',
        max_length=60,
    )
    description = forms.CharField(
        label='Describe your case study or project:',
        help_text=(
            'Describe the project or case study in 1,000 characters or fewer. '
            'Make sure you use this space to demonstrate the value of your '
            'company to an international business audience.'
        ),
        max_length=1000,
        widget=forms.Textarea,
    )
    sector = forms.ChoiceField(
        choices=choices.COMPANY_CLASSIFICATIONS,
    )
    website = forms.URLField(
        label='Web link for your case study (optional):',
        help_text='Use a full web address (URL) including http:// or https://',
        max_length=255,
        required=False
    )
    keywords = forms.CharField(
        label=(
            'Enter up to 10 keywords that describe your case study '
            '(separated by commas):'
        ),
        help_text=(
            'These keywords will be used to help potential overseas buyers '
            'find your case study.'
        ),
        max_length=1000,
        widget=forms.Textarea,
        validators=[shared_validators.keywords_word_limit]
    )


class CaseStudyRichMediaForm(IndentedInvalidFieldsMixin, AutoFocusFieldMixin,
                             forms.Form):
    image_one = forms.FileField(
        required=False,
        validators=[shared_validators.case_study_image_filesize]
    )
    image_two = forms.FileField(
        required=False,
        validators=[shared_validators.case_study_image_filesize]
    )
    image_three = forms.FileField(
        required=False,
        validators=[shared_validators.case_study_image_filesize]
    )
    testimonial = forms.CharField(
        max_length=1000,
        required=False,
        widget=forms.Textarea,
    )
    testimonial_name = forms.CharField(
        label="Source - full name",
        help_text="The name of the person who gave the testimonial",
        max_length=255,
        required=False,
    )
    testimonial_job_title = forms.CharField(
        label="Source - job title",
        help_text="The job title of the person who gave the testimonial",
        max_length=255,
        required=False,
    )
    testimonial_company = forms.CharField(
        label="Source - company name",
        help_text="The company of the person who gave the testimonial",
        max_length=255,
        required=False,
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
        validators=[shared_validators.keywords_word_limit]
    )
    employees = forms.ChoiceField(
        choices=choices.EMPLOYEES,
        label='How many employees are in your company?',
        help_text=(
            'Tell international buyers more about your business to ensure '
            'the right buyers can find you.'
        )
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


class CompanyClassificationForm(AutoFocusFieldMixin,
                                IndentedInvalidFieldsMixin, forms.Form):
    sectors = forms.MultipleChoiceField(
        label=(
            'What sectors is your company interested in working in? '
            'Choose no more than 10 sectors.'
        ),
        choices=choices.COMPANY_CLASSIFICATIONS,
        widget=forms.CheckboxSelectMultiple(),
        validators=[shared_validators.sector_choice_limit]
    )


class CompanyContactDetailsForm(AutoFocusFieldMixin,
                                IndentedInvalidFieldsMixin,
                                forms.Form):

    error_messages = {
        'different': 'Your emails do not match.'
    }

    email_full_name = forms.CharField(
        label='Contact name for buyer enquiries:',
        max_length=200,
        help_text=(
            'This is the full name of the person that international buyers '
            'should use when contacting your company.'
        ),
    )
    email_address = forms.EmailField(
        label='Contact email address',
        help_text=(
            'This is the email address that international buyers should use'
            ' when contacting your company.'
        ),
    )


class PreventTamperMixin(forms.Form):

    NO_TAMPER_MESSAGE = 'Form tamper detected.'

    signature = forms.CharField(
        widget=forms.HiddenInput
    )

    def __init__(self, initial=None, *args, **kwargs):
        fields = self.tamper_proof_fields
        assert fields
        # `self.tamper_proof_fields` must use data type that preserves order
        assert isinstance(fields, list) or isinstance(fields, tuple)
        initial = initial or {}
        initial['signature'] = self.create_signature(initial)
        super().__init__(initial=initial, *args, **kwargs)

    def create_signature(self, values):
        value = [values.get(field, '') for field in self.tamper_proof_fields]
        return Signer().sign(','.join(value))

    def is_form_tampered(self):
        data = self.cleaned_data
        return data.get('signature') != self.create_signature(data)

    def clean(self):
        data = super().clean()
        if self.is_form_tampered():
            raise forms.ValidationError(self.NO_TAMPER_MESSAGE)
        return data


class CompanyAddressVerificationForm(PreventTamperMixin,
                                     AutoFocusFieldMixin,
                                     IndentedInvalidFieldsMixin,
                                     forms.Form):

    tamper_proof_fields = [
        'address_line_1',
        'address_line_2',
        'locality',
        'country',
        'postal_code',
        'po_box',
    ]

    postal_full_name = forms.CharField(
        label='Full name:',
        max_length=255,
        help_text='This is the full name that letters will be addressed to.',
        required=False,
    )
    address_line_1 = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
    )
    address_line_2 = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
    )
    locality = forms.CharField(
        label='City:',
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
    )
    country = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
    )
    postal_code = forms.CharField(
        label='Postcode:',
        max_length=200,
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
    )
    po_box = forms.CharField(
        label='PO box',
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
    )


class CompanyCodeVerificationForm(AutoFocusFieldMixin,
                                  IndentedInvalidFieldsMixin,
                                  forms.Form):

    error_messages = {
        'different': 'Incorrect code.'
    }

    code = forms.CharField(
        label=(
            'Enter the verification code from the letter we sent to you after '
            ' you created your company profile:'
        ),
        help_text=mark_safe(
            'We sent you a letter through the mail containing a twelve digit '
            'code.'
        ),
        max_length=12,
        min_length=12,
    )

    def __init__(self, *args, **kwargs):
        sso_id = kwargs.pop('sso_id')
        super().__init__(*args, **kwargs)
        self.fields['code'].validators = halt_validation_on_failure(
            validators.verify_with_code(sso_id=sso_id),
            *self.fields['code'].validators
        )


class EmptyForm(forms.Form):
    # django form tools expects a form for every step - even if we want it to
    # simply be an interstitial page.
    pass


def serialize_supplier_case_study_forms(cleaned_data):
    """
    Return the shape directory-api-client expects for creating and updating
    supplier case studies.

    @param {dict} cleaned_data - All the fields in `CaseStudyRichMediaForm` and
                                `CaseStudyBasicInfoForm`
    @returns dict

    """

    data = {
        'title': cleaned_data['title'],
        'description': cleaned_data['description'],
        'sector': cleaned_data['sector'],
        'website': cleaned_data['website'],
        'keywords': cleaned_data['keywords'],
        'testimonial': cleaned_data['testimonial'],
        'testimonial_name': cleaned_data['testimonial_name'],
        'testimonial_job_title': cleaned_data['testimonial_job_title'],
        'testimonial_company': cleaned_data['testimonial_company'],
    }
    # the case studies edit view pre-populates the image fields with the url of
    # the existing value (rather than the real file). Things would get
    # confused if we send a string instead of a file here.
    for field in ['image_one', 'image_two', 'image_three']:
        if not isinstance(cleaned_data[field], str):
            data[field] = cleaned_data[field]
    return data


def serialize_company_profile_forms(cleaned_data):
    """
    Return the shape directory-api-client expects for company profile edit.

    @param {dict} cleaned_data - All the fields in `CompanyBasicInfoForm`
                                 `CompanyLogoForm`,
                                 `CompanyClassificationForm`,
                                 `CompanyContactDetailsForm`, and
                                 `CompanyAddressVerificationForm`.
    @returns dict

    """

    return {
        'name': cleaned_data['name'],
        'website': cleaned_data['website'],
        'keywords': cleaned_data['keywords'],
        'employees': cleaned_data['employees'],
        'sectors': cleaned_data['sectors'],
        'contact_details': {
            'address_line_1': cleaned_data['address_line_1'],
            'address_line_2': cleaned_data['address_line_2'],
            'country': cleaned_data['country'],
            'email_address': cleaned_data['email_address'],
            'email_full_name': cleaned_data['email_full_name'],
            'locality': cleaned_data['locality'],
            'po_box': cleaned_data['po_box'],
            'postal_code': cleaned_data['postal_code'],
            'postal_full_name': cleaned_data['postal_full_name'],
        }
    }


def serialize_company_logo_form(cleaned_data):
    """
    Return the shape directory-api-client expects for changing logo.

    @param {dict} cleaned_data - All the fields in `CompanyLogoForm`
    @returns dict

    """

    return {
        'logo': cleaned_data['logo'],
    }


def serialize_company_description_form(cleaned_data):
    """
    Return the shape directory-api-client expects for changing description.

    @param {dict} cleaned_data - All the fields in `CompanyDescriptionForm`
    @returns dict

    """

    return {
        'description': cleaned_data['description'],
    }


def serialize_company_basic_info_form(cleaned_data):
    """
    Return the shape directory-api-client expects for updating basic info.

    @param {dict} cleaned_data - All the fields in `CompanyBasicInfoForm`
    @returns dict

    """

    return {
        'name': cleaned_data['name'],
        'website': cleaned_data['website'],
        'keywords': cleaned_data['keywords'],
        'employees': cleaned_data['employees'],
    }


def serialize_company_sectors_form(cleaned_data):
    """
    Return the shape directory-api-client expects for updating classifications.

    @param {dict} cleaned_data - All the fields in `CompanyClassificationForm`
    @returns dict

    """

    return {
        'sectors': cleaned_data['sectors'],
    }


def serialize_company_contact_form(cleaned_data):
    """
    Return the shape directory-api-client expects for updating contact details.

    @param {dict} cleaned_data - All the fields in `CompanyContactDetailsForm`
    @returns dict

    """

    return {
        'contact_details': {
            'email_full_name': cleaned_data['email_full_name'],
            'email_address': cleaned_data['email_address'],
        }
    }


def serialize_company_address_form(cleaned_data):
    """
    Return the shape directory-api-client expects for updating address.

    @param {dict} cleaned_data - All the fields in
                                 `CompanyAddressVerificationForm`
    @returns dict

    """

    return {
        'contact_details': {
            'address_line_1': cleaned_data['address_line_1'],
            'address_line_2': cleaned_data['address_line_2'],
            'country': cleaned_data['country'],
            'locality': cleaned_data['locality'],
            'po_box': cleaned_data['po_box'],
            'postal_code': cleaned_data['postal_code'],
            'postal_full_name': cleaned_data['postal_full_name'],
        }
    }


def is_optional_profile_values_set(company_profile):
    """
    Return True if the fields set in `CompanyBasicInfoForm` ,
    `CompanyClassificationForm`, `CompanyContactDetailsForm`
    `CompanyAddressVerificationForm` are present in the company profile.

    """

    fields = [
        'name',
        'website',
        'sectors',
        'keywords',
        'employees',
        # CompanyAddressVerificationForm and CompanyContactDetailsForm fields
        # are stored in `contact_details`.
        'contact_details',
    ]
    return all(company_profile.get(field) for field in fields)
