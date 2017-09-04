from directory_validators import company as shared_validators
from directory_validators import enrolment as shared_enrolment_validators
from directory_constants.constants import choices

from django import forms
from django.conf import settings
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe

from company import validators
from enrolment.forms import IndentedInvalidFieldsMixin, AutoFocusFieldMixin
from enrolment.helpers import halt_validation_on_failure
from enrolment.widgets import (
    CheckboxSelectInlineLabelMultiple,
    CheckboxWithInlineLabel
)
from enrolment.helpers import CompaniesHouseClient


class SocialLinksForm(IndentedInvalidFieldsMixin, AutoFocusFieldMixin,
                      forms.Form):

    linkedin_url = forms.URLField(
        label='URL for your LinkedIn company profile (optional):',
        help_text='Use a full web address (URL) including http:// or https://',
        max_length=255,
        required=False,
        validators=[shared_validators.case_study_social_link_linkedin],
    )
    twitter_url = forms.URLField(
        label='URL for your Twitter company profile (optional):',
        help_text='Use a full web address (URL) including http:// or https://',
        max_length=255,
        required=False,
        validators=[shared_validators.case_study_social_link_twitter],
    )
    facebook_url = forms.URLField(
        label='URL for your Facebook company page (optional):',
        help_text='Use a full web address (URL) including http:// or https://',
        max_length=255,
        required=False,
        validators=[shared_validators.case_study_social_link_facebook],
    )


class PublicProfileSearchForm(IndentedInvalidFieldsMixin, AutoFocusFieldMixin,
                              forms.Form):
    sectors = forms.ChoiceField(
        choices=choices.INDUSTRIES,
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
        label='Title of your case study or project',
        help_text='Give your case study a title of 60 characters or fewer.',
        max_length=60,
        validators=[shared_validators.no_html],
    )
    short_summary = forms.CharField(
        label='Summary of your case study or project',
        help_text=(
            'Summarise your case study in 50 words or fewer. This will'
            ' appear on your main trade profile page.'
        ),
        max_length=200,
        validators=[
            validators.does_not_contain_email,
            shared_validators.no_html,
        ],
        widget=forms.Textarea,
    )
    description = forms.CharField(
        label='Describe your case study or project',
        help_text=(
            'Describe the project or case study in 1,000 characters or fewer. '
            'Use this space to demonstrate the value of your '
            'company to an international business audience.'
        ),
        max_length=1000,
        validators=[
            validators.does_not_contain_email,
            shared_validators.no_html,
        ],
        widget=forms.Textarea,
    )
    sector = forms.ChoiceField(
        help_text=(
            'Select the sector most relevant to your case study or project.'
        ),
        choices=[('', 'Select Sector')] + list(choices.INDUSTRIES)
    )
    website = forms.URLField(
        label='The web address for your case study (optional)',
        help_text='Enter a full URL including http:// or https://',
        max_length=255,
        required=False,
    )
    keywords = forms.CharField(
        label=(
            'Enter up to 10 keywords that describe your case study. '
            'Keywords should be separated by commas.'
        ),
        help_text=(
            'These keywords will be used to help potential overseas buyers '
            'find your case study.'
        ),
        max_length=1000,
        widget=forms.Textarea,
        validators=[
            shared_validators.keywords_word_limit,
            shared_validators.keywords_special_characters,
            shared_validators.no_html,
        ]
    )


class DynamicHelptextFieldsMixin:
    """
    Set the help_text and label to different values depending on if
    the field has an initial value.

    """

    def __init__(self, *args, **kwargs):
        assert hasattr(self, 'help_text_maps')
        super().__init__(*args, **kwargs)
        self.set_help_text()

    def set_help_text(self):
        for help_text_map in self.help_text_maps:
            field = self[help_text_map['field_name']]
            if self.initial.get(field.name):
                help_text = help_text_map['update_help_text'].format(
                    initial_value=self.initial.get(field.name)
                )
                field.help_text = help_text
                field.label = help_text_map['update_label']
            else:
                field.help_text = help_text_map['create_help_text']
                field.label = help_text_map['create_label']


class CaseStudyRichMediaForm(IndentedInvalidFieldsMixin, AutoFocusFieldMixin,
                             DynamicHelptextFieldsMixin, forms.Form):

    image_help_text_create = (
        'This image will be shown at full width on your case study page and '
        'must be at least 700 pixels wide and in landscape format. For best '
        'results, upload an image at 1820 x 682 pixels.'
    )
    image_help_text_update = (
        'Select a different image to replace the '
        '<a href="{initial_value}" target="_blank" alt="View current image">'
        'current one</a>. ' + image_help_text_create
    )
    help_text_maps = [
        {
            'field_name': 'image_one',
            'create_help_text': image_help_text_create,
            'update_help_text': image_help_text_update,
            'create_label': 'Upload main image for this case study',
            'update_label': (
                'Replace the main image for this case study (optional)'
            )
        },
        {
            'field_name': 'image_two',
            'create_help_text': image_help_text_create,
            'update_help_text': image_help_text_update,
            'create_label': 'Upload a second image (optional)',
            'update_label': 'Replace the second image (optional)',
        },
        {
            'field_name': 'image_three',
            'create_help_text': image_help_text_create,
            'update_help_text': image_help_text_update,
            'create_label': 'Upload a third image (optional)',
            'update_label': 'Replace the third image (optional)',
        },
    ]

    image_one = forms.ImageField(
        validators=[
            shared_validators.case_study_image_filesize,
            shared_validators.image_format,
        ],
    )
    image_one_caption = forms.CharField(
        label=(
            'Add a caption that tells visitors what the main image represents'
        ),
        help_text='Maximum 120 characters',
        max_length=120,
        widget=forms.Textarea,
        validators=[shared_validators.no_html],
    )
    image_two = forms.ImageField(
        required=False,
        validators=[
            shared_validators.case_study_image_filesize,
            shared_validators.image_format,
        ]
    )
    image_two_caption = forms.CharField(
        label=(
            'Add a caption that tells visitors what this second image '
            'represents'
        ),
        help_text='Maximum 120 characters',
        max_length=120,
        widget=forms.Textarea,
        required=False,
        validators=[shared_validators.no_html],
    )
    image_three = forms.ImageField(
        required=False,
        validators=[
            shared_validators.case_study_image_filesize,
            shared_validators.image_format,
        ]
    )
    image_three_caption = forms.CharField(
        label=(
            'Add a caption that tells visitors what this third image '
            'represents'
        ),
        help_text='Maximum 120 characters',
        max_length=120,
        widget=forms.Textarea,
        required=False,
        validators=[shared_validators.no_html],
    )
    testimonial = forms.CharField(
        label='Testimonial or block quote (optional)',
        help_text=(
            'Add testimonial from a satisfied client or use this space'
            ' to highlight an important part of your case study.'
        ),
        max_length=1000,
        required=False,
        widget=forms.Textarea,
        validators=[shared_validators.no_html],
    )
    testimonial_name = forms.CharField(
        label='Full name of the source of the testimonial (optional)',
        help_text=(
            'Add the source to make the quote more credible and to '
            'help buyers understand the importance of the testimonial.'
        ),
        max_length=255,
        required=False,
        validators=[shared_validators.no_html],
    )
    testimonial_job_title = forms.CharField(
        label='Job title of the source (optional)',
        max_length=255,
        required=False,
        validators=[shared_validators.no_html],
    )
    testimonial_company = forms.CharField(
        label="Company name of the source (optional)",
        max_length=255,
        required=False,
        validators=[shared_validators.no_html],
    )


class CompanyBasicInfoForm(AutoFocusFieldMixin, IndentedInvalidFieldsMixin,
                           forms.Form):
    name = forms.CharField(
        label='Company name',
        help_text=(
            'Enter your preferred business name'
        ),
        max_length=255,
        validators=[shared_validators.no_html],
    )
    website = forms.URLField(
        label='Website (optional):',
        max_length=255,
        help_text=(
            'The website address must start with either http:// or '
            'https://'
        ),
        required=False,
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
        validators=[
            shared_validators.keywords_special_characters,
            shared_validators.keywords_word_limit,
            shared_validators.no_html,
        ]
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
    summary = forms.CharField(
        label='Brief summary to make your company stand out to buyers:',
        help_text='Maximum 250 characters.',
        max_length=250,
        widget=forms.Textarea,
        validators=[
            validators.does_not_contain_email,
            shared_validators.no_html,
        ],
    )
    description = forms.CharField(
        widget=forms.Textarea,
        label='Describe your business to overseas buyers:',
        help_text='Maximum 2,000 characters.',
        max_length=2000,
        validators=[
            validators.does_not_contain_email,
            shared_validators.no_html,
        ],
    )


class CompanyLogoForm(AutoFocusFieldMixin, IndentedInvalidFieldsMixin,
                      forms.Form):
    logo = forms.ImageField(
        help_text=(
            'For best results this should be a transparent PNG file of 600 x '
            '600 pixels and no more than {0}MB'.format(
                int(settings.VALIDATOR_MAX_LOGO_SIZE_BYTES / 1024 / 1014)
            )
        ),
        required=True,
        validators=[
            shared_enrolment_validators.logo_filesize,
            shared_validators.image_format,
        ]
    )


class CompanyClassificationForm(AutoFocusFieldMixin,
                                IndentedInvalidFieldsMixin, forms.Form):
    sectors = forms.ChoiceField(
        label=(
            'What industry is your company in?'
        ),
        choices=choices.INDUSTRIES,
    )
    export_destinations = forms.MultipleChoiceField(
        label='Select the countries you would like to export to',
        choices=choices.EXPORT_DESTINATIONS + (('', 'Other'),),
        widget=CheckboxSelectInlineLabelMultiple,
    )
    export_destinations_other = forms.CharField(
        label='Other countries',
        max_length=1000,
        help_text='Enter 3 maximum',
        required=False,
        validators=[shared_validators.no_html],
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
        validators=[shared_validators.no_html]
    )
    email_address = forms.EmailField(
        label='Contact email address',
        help_text=(
            'This is the email address that international buyers'
            ' will see to contact your company.'
        ),
    )
    website = forms.URLField(
        label='Website (optional):',
        max_length=255,
        help_text=(
            'The website address must start with either http:// or '
            'https://'
        ),
        required=False,
    )


class CompanyAddressVerificationForm(AutoFocusFieldMixin,
                                     IndentedInvalidFieldsMixin,
                                     forms.Form):

    postal_full_name = forms.CharField(
        label='Add your name',
        max_length=255,
        help_text='This is the full name that letters will be addressed to.',
        validators=[shared_validators.no_html],
    )
    address_confirmed = forms.BooleanField(
        label='',
        widget=CheckboxWithInlineLabel(
            label=mark_safe(
                '<span>Tick to confirm address.</span> '
                '<small> If you can’t collect the letter yourself, you’ll '
                'need to make sure someone can send it on to you.</small>'
            ),
        ),
    )

    def visible_fields(self):
        skip = ['postal_full_name']
        return [
            field for field in self
            if not field.is_hidden and field.name not in skip
        ]


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
        sso_session_id = kwargs.pop('sso_session_id')
        super().__init__(*args, **kwargs)
        self.fields['code'].validators = halt_validation_on_failure(
            validators.verify_with_code(sso_session_id=sso_session_id),
            *self.fields['code'].validators
        )


class CompaniesHouseOauth2Form(forms.Form):
    MESSAGE_INVALID_CODE = 'Invalid code.'

    code = forms.CharField(max_length=1000)

    def __init__(self, redirect_uri, *args, **kwargs):
        self.redirect_uri = redirect_uri
        super().__init__(*args, **kwargs)

    @cached_property
    def oauth2_response(self):
        return CompaniesHouseClient.verify_oauth2_code(
            code=self.cleaned_data['code'],
            redirect_url=self.redirect_uri
        )

    def clean_code(self):
        if not self.oauth2_response.ok:
            raise forms.ValidationError(self.MESSAGE_INVALID_CODE)
        return self.cleaned_data['code']


class AddCollaboratorForm(AutoFocusFieldMixin, forms.Form):
    email_address = forms.EmailField(
        label=(
            'Enter the email address you would like to add to your account'
        ),
        widget=forms.EmailInput(
            attrs={'placeholder': 'Email address'}
        )
    )


class RemoveCollaboratorForm(AutoFocusFieldMixin, forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_ids'].choices = self.get_user_ids_choices()

    def get_user_ids_choices(self):
        return (
            (1, 'test@axample.com'),
        )

    user_ids = forms.MultipleChoiceField(
        label='Select the email/emails you would like to remove',
        choices=[],  # updated on __init__
        widget=CheckboxSelectInlineLabelMultiple,
    )


class TransferAccountEmailForm(AutoFocusFieldMixin, forms.Form):
    email_address = forms.EmailField(
        label=(
            'Enter the email address you would like to take over your account'
        ),
        widget=forms.EmailInput(
            attrs={'placeholder': 'Email address'}
        )
    )


class TransferAccountPasswordForm(AutoFocusFieldMixin, forms.Form):
    password = forms.CharField(
        label='Your password',
        help_text='For your security, please enter your current password',
        widget=forms.PasswordInput,
    )


class EmptyForm(forms.Form):
    # some views expect a form, even if no data entry is required. This works
    # around this requirement.
    pass


def serialize_case_study_forms(cleaned_data):
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
        'short_summary': cleaned_data['short_summary'],
        'image_one_caption': cleaned_data['image_one_caption'],
        'image_two_caption': cleaned_data['image_two_caption'],
        'image_three_caption': cleaned_data['image_three_caption'],
    }
    # the case studies edit view pre-populates the image fields with the url of
    # the existing value (rather than the real file). Things would get
    # confused if we send a string instead of a file here.
    for field in ['image_one', 'image_two', 'image_three']:
        if cleaned_data[field] and not isinstance(cleaned_data[field], str):
            data[field] = cleaned_data[field]
    return data


def serialize_company_profile_forms(cleaned_data):
    """
    Return the shape directory-api-client expects for company profile edit.

    @param {dict} cleaned_data - All the fields in `CompanyBasicInfoForm`
                                 `CompanyLogoForm`,
                                 `CompanyClassificationForm`, and
                                 `CompanyAddressVerificationForm`.
    @returns dict

    """

    return {
        'name': cleaned_data['name'],
        'website': cleaned_data['website'],
        'keywords': cleaned_data['keywords'],
        'employees': cleaned_data['employees'],
        'export_destinations': cleaned_data['export_destinations'],
        'export_destinations_other': cleaned_data['export_destinations_other'],
        'sectors': [cleaned_data['sectors']],
        'postal_full_name': cleaned_data['postal_full_name'],

    }


def serialize_company_profile_without_address_forms(cleaned_data):
    """
    Return the shape directory-api-client expects for company profile edit,
    excluding address fields.

    @param {dict} cleaned_data - All the fields in `CompanyBasicInfoForm`
                                 `CompanyLogoForm`, and
                                 `CompanyClassificationForm`
    @returns dict

    """

    return {
        'name': cleaned_data['name'],
        'website': cleaned_data['website'],
        'keywords': cleaned_data['keywords'],
        'employees': cleaned_data['employees'],
        'export_destinations': cleaned_data['export_destinations'],
        'export_destinations_other': cleaned_data['export_destinations_other'],
        'sectors': [cleaned_data['sectors']],
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
        'summary': cleaned_data['summary']
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
        'sectors': [cleaned_data['sectors']],
        'export_destinations': cleaned_data['export_destinations'],
        'export_destinations_other': cleaned_data['export_destinations_other'],
    }


def serialize_company_contact_form(cleaned_data):
    """
    Return the shape directory-api-client expects for updating contact details.

    @param {dict} cleaned_data - All the fields in `CompanyContactDetailsForm`
    @returns dict

    """

    return {
        'email_full_name': cleaned_data['email_full_name'],
        'email_address': cleaned_data['email_address'],
        'website': cleaned_data['website'],
    }


def serialize_company_address_form(cleaned_data):
    """
    Return the shape directory-api-client expects for updating address.

    @param {dict} cleaned_data - All the fields in
                                 `CompanyAddressVerificationForm`
    @returns dict

    """

    return {
        'postal_full_name': cleaned_data['postal_full_name'],
    }


def serialize_social_links_form(cleaned_data):

    """
    Return the shape directory-api-client expects for updating social links.

    @param {dict} cleaned_data - All the fields in `SocialLinksForm`
    @returns dict

    """
    return {
        'facebook_url': cleaned_data['facebook_url'],
        'twitter_url': cleaned_data['twitter_url'],
        'linkedin_url': cleaned_data['linkedin_url'],
    }


def is_optional_profile_values_set(company_profile):
    """
    Return True if the fields set in `CompanyBasicInfoForm` ,
    `CompanyClassificationForm`, `CompanyContactDetailsForm`
    `CompanyAddressVerificationForm` are present in the company profile.

    """

    fields = ['sectors', 'keywords', 'employees']
    # pre-verified companies do not need to provide address details
    if company_profile['verified_with_preverified_enrolment'] is False:
        fields.append('postal_full_name',)
    return all(company_profile.get(field) for field in fields)
