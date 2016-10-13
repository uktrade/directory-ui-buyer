from io import BytesIO

import pytest

from django import forms
from django.core.files.uploadedfile import InMemoryUploadedFile

from registration import validators


def create_file_of_size(size):
    return InMemoryUploadedFile(
        file=BytesIO(b''),
        field_name=None,
        name='logo.png',
        content_type='image/png',
        size=size,
        charset=None
    )


def test_validate_logo_filesize_rejects_too_big(settings):
    settings.MAX_LOGO_SIZE_BYTES = 100
    with pytest.raises(forms.ValidationError):
        assert validators.validate_logo_filesize(create_file_of_size(101))


def test_validate_logo_filesize_accepts_not_too_big(settings):
    settings.MAX_LOGO_SIZE_BYTES = 100
    assert validators.validate_logo_filesize(create_file_of_size(100)) is None
