from directory_validators import company as shared_validators
from directory_components.forms import (
    BooleanField, CheckboxSelectInlineLabelMultiple
)

from django import forms
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe

from directory_api_client.client import api_client
from company import helpers, validators

from enrolment.helpers import CompaniesHouseClient

from directory_sso_api_client.client import sso_api_client


class IndentedInvalidFieldsMixin:
    error_css_class = 'input-field-container has-error'


class AutoFocusFieldMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fields = self.visible_fields()
        if fields:
            field = fields[0]
            self.fields[field.name].widget.attrs['autofocus'] = 'autofocus'


class CompanyAddressVerificationForm(AutoFocusFieldMixin,
                                     IndentedInvalidFieldsMixin,
                                     forms.Form):

    postal_full_name = forms.CharField(
        label='Add your name',
        max_length=255,
        help_text='This is the full name that letters will be addressed to.',
        validators=[shared_validators.no_html],
    )
    address_confirmed = BooleanField(
        label=mark_safe(
            '<span>Tick to confirm address.</span> '
            '<small> If you can’t collect the letter yourself, you’ll '
            'need to make sure someone can send it on to you.</small>'
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
        label='',
        max_length=12,
        min_length=12,
    )

    def __init__(self, *args, **kwargs):
        sso_session_id = kwargs.pop('sso_session_id')
        super().__init__(*args, **kwargs)
        self.fields['code'].validators = helpers.halt_validation_on_failure(
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
            redirect_uri=self.redirect_uri
        )

    def clean_code(self):
        if not self.oauth2_response.ok:
            raise forms.ValidationError(self.MESSAGE_INVALID_CODE)
        return self.cleaned_data['code']


class BaseMultiUserEmailForm(
    AutoFocusFieldMixin, IndentedInvalidFieldsMixin, forms.Form
):
    MESSAGE_CANNOT_SEND_TO_SELF = 'Please enter a different email address'

    def __init__(self, sso_email_address, *args, **kwargs):
        self.sso_email_address = sso_email_address
        super().__init__(*args, **kwargs)

    def clean_email_address(self):
        if self.cleaned_data['email_address'] == self.sso_email_address:
            raise forms.ValidationError(self.MESSAGE_CANNOT_SEND_TO_SELF)
        return self.cleaned_data['email_address']


class AddCollaboratorForm(BaseMultiUserEmailForm):

    email_address = forms.EmailField(
        label=(
            'Enter the new editor’s email address.'
        ),
        widget=forms.EmailInput(
            attrs={'placeholder': 'Email address'}
        )
    )


class RemoveCollaboratorForm(AutoFocusFieldMixin, forms.Form):

    def __init__(self, sso_session_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sso_ids'].choices = self.get_supplier_ids_choices(
            sso_session_id=sso_session_id
        )

    def get_supplier_ids_choices(self, sso_session_id):
        response = api_client.company.collaborator_list(
            sso_session_id=sso_session_id
        )
        response.raise_for_status()
        parsed = response.json()
        return [(i['sso_id'], i['company_email']) for i in parsed]

    sso_ids = forms.MultipleChoiceField(
        label='',
        choices=[],  # updated on __init__
        widget=CheckboxSelectInlineLabelMultiple,
    )


class TransferAccountEmailForm(BaseMultiUserEmailForm):

    email_address = forms.EmailField(
        label=(
            'Enter the email address of the new administrator.'
        ),
        widget=forms.EmailInput(
            attrs={'placeholder': 'Email address'}
        )
    )


class TransferAccountPasswordForm(
    IndentedInvalidFieldsMixin, AutoFocusFieldMixin, forms.Form
):
    MESSAGE_INVALID_PASSWORD = 'Invalid password'
    use_required_attribute = False

    password = forms.CharField(
        label='Your password',
        help_text='For your security, please enter your current password',
        widget=forms.PasswordInput,
    )

    def __init__(self, sso_session_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sso_session_id = sso_session_id

    def clean_password(self):
        response = sso_api_client.user.check_password(
            session_id=self.sso_session_id,
            password=self.cleaned_data['password'],
        )
        if not response.ok:
            raise forms.ValidationError(self.MESSAGE_INVALID_PASSWORD)
        return self.cleaned_data['password']


class AcceptInviteForm(forms.Form):
    invite_key = forms.CharField(
        widget=forms.HiddenInput
    )


class EmptyForm(forms.Form):
    # some views expect a form, even if no data entry is required. This works
    # around this requirement.
    pass


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
