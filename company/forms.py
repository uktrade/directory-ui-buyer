from django import forms
from django.conf import settings

from directory_validators import company as shared_validators
from directory_validators import enrolment as shared_enrolment_validators
from directory_validators.constants import choices

from enrolment.forms import IndentedInvalidFieldsMixin, AutoFocusFieldMixin


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
        max_length=100,
    )
    description = forms.CharField(
        max_length=1000,
        widget=forms.Textarea,
    )
    sector = forms.ChoiceField(
        choices=choices.COMPANY_CLASSIFICATIONS,
    )
    website = forms.URLField(
        max_length=255,
        required=False
    )
    year = forms.CharField(max_length=4)
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
    email_address = forms.EmailField(
        help_text=(
            'This is the email address that international buyers should use'
            ' when contacting your company.'
        ),
    )
    email_full_name = forms.CharField(
        label='Full name:',
        max_length=200,
        help_text=(
            'This is the full name that international buyers should use'
            ' when contacting your company.'
        ),
    )


class CompanyAddressVerificationForm(AutoFocusFieldMixin,
                                     IndentedInvalidFieldsMixin,
                                     forms.Form):
    postal_full_name = forms.CharField(
        label='Full name:',
        max_length=255,
        help_text='This is the full name that letters will be addressed to.',
        required=False,
    )
    address_line_1 = forms.CharField(max_length=255)
    address_line_2 = forms.CharField(max_length=255, required=False)
    locality = forms.CharField(label='City:', max_length=255, required=False)
    country = forms.CharField(max_length=255, required=False)
    postal_code = forms.CharField(max_length=255)
    po_box = forms.CharField(max_length=255, required=False)


def serialize_supplier_case_study_forms(cleaned_data):
    """
    Return the shape directory-api-client expects for creating and updating
    supplier case studies.

    @param {dict} cleaned_data - All the fields in `CaseStudyRichMediaForm` and
                                `CaseStudyBasicInfoForm`
    @returns dict

    """

    return {
        'title': cleaned_data['title'],
        'description': cleaned_data['description'],
        'sector': cleaned_data['sector'],
        'website': cleaned_data['website'],
        'year': cleaned_data['year'],
        'keywords': cleaned_data['keywords'],
        'image_one': cleaned_data['image_one'],
        'image_two': cleaned_data['image_two'],
        'image_three': cleaned_data['image_three'],
        'testimonial': cleaned_data['testimonial'],
    }


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
