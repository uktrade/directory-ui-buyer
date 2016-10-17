from django import forms
from django.conf import settings

from registration.clients.directory_api import api_client


MESSAGE_FILE_TOO_BIG = 'File is too big.'
MESSAGE_USE_CORPORATE_EMAIL = 'Plase use your corporate email address.'


def validate_logo_filesize(value):
    if value.size > settings.MAX_LOGO_SIZE_BYTES:
        raise forms.ValidationError(MESSAGE_FILE_TOO_BIG)


def email_domain(value):
    if not api_client.is_email_address_valid(value):
        raise forms.ValidationError(MESSAGE_USE_CORPORATE_EMAIL)
