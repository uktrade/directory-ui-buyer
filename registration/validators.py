from django import forms
from django.conf import settings


max_logo_bytes = settings.MAX_LOGO_SIZE_MEGABYTES * 1024 * 1024


def validate_logo_filesize(value):
    if value.size > max_logo_bytes:
        raise forms.ValidationError('File is too big.')
