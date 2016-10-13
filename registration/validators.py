from django import forms
from django.conf import settings


MESSAGE_FILE_TOO_BIG = 'File is too big.'


def validate_logo_filesize(value):
    if value.size > settings.MAX_LOGO_SIZE_BYTES:
        raise forms.ValidationError(MESSAGE_FILE_TOO_BIG)
