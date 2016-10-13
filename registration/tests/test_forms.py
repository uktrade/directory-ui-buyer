from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings

from registration import constants, forms, validators


def create_file_of_size(size):
    return InMemoryUploadedFile(
        file=BytesIO(b''),
        field_name=None,
        name='logo.png',
        content_type='image/png',
        size=size,
        charset=None
    )


def test_step_one_rejects_missing_data():
    form = forms.CompanyForm(data={})
    assert form.is_valid() is False
    assert 'company_number' in form.errors


def test_step_one_rejects_too_long_company_number():
    form = forms.CompanyForm(data={
        'company_number': '012456789',
    })
    assert form.is_valid() is False
    assert 'company_number' in form.errors


def test_step_one_rejects_too_short_company_number():
    form = forms.CompanyForm(data={
        'company_number': '0124567',
    })
    assert form.is_valid() is False
    assert 'company_number' in form.errors


def test_step_one_accepts_valid_data():
    form = forms.CompanyForm(data={
        'company_number': '01245678',
    })
    assert form.is_valid() is True


def test_step_two_accepts_valid_data():
    form = forms.AimsForm(data={
        'aim_one': constants.AIMS[1][0],
        'aim_two': constants.AIMS[2][0],
    })
    assert form.is_valid()


def test_step_two_rejects_no_aims():
    form = forms.AimsForm(data={
        'aim_one': '',
        'aim_two': '',
    })
    assert form.is_valid() is False


def test_step_three_rejects_missing_data():
    form = forms.UserForm(data={})
    assert 'name' in form.errors
    assert 'password' in form.errors
    assert 'terms_agreed' in form.errors
    assert 'email' in form.errors


def test_step_three_rejects_invalid_email_addresses():
    form = forms.UserForm(data={
        'email': 'johnATjones.com',
    })
    assert form.is_valid() is False
    assert 'email' in form.errors


def test_step_three_accepts_valid_data():
    form = forms.UserForm(data={
        'name': 'John Johnson',
        'password': 'hunter2',
        'terms_agreed': 1,
        'email': 'john@jones.com',
    })
    assert form.is_valid()


def test_company_profile_form_requires_name():
    form = forms.CompanyBasicInfoForm(data={})

    valid = form.is_valid()

    assert valid is False
    assert 'company_name' in form.errors
    assert len(form.errors['company_name']) == 1
    assert form.errors['company_name'][0] == 'This field is required.'


def test_company_profile_form_requires_description():
    form = forms.CompanyBasicInfoForm(data={})

    valid = form.is_valid()

    assert valid is False
    assert 'description' in form.errors
    assert len(form.errors['description']) == 1
    assert form.errors['description'][0] == 'This field is required.'


def test_company_profile_form_requires_website():
    form = forms.CompanyBasicInfoForm(data={})

    valid = form.is_valid()

    assert valid is False
    assert 'website' in form.errors
    assert len(form.errors['website']) == 1
    assert form.errors['website'][0] == 'This field is required.'


def test_company_profile_form_rejects_invalid_website():
    form = forms.CompanyBasicInfoForm(data={'website': 'google'})

    valid = form.is_valid()

    assert valid is False
    assert 'website' in form.errors
    assert len(form.errors['website']) == 1
    assert form.errors['website'][0] == 'Enter a valid URL.'


def test_company_profile_form_accepts_valid_data():
    logo = create_file_of_size(settings.MAX_LOGO_SIZE_BYTES)
    data = {'company_name': 'Amazon UK',
            'website': 'http://amazon.co.uk',
            'description': 'Ecommerce'}
    form = forms.CompanyBasicInfoForm(data=data, files={'logo': logo})

    valid = form.is_valid()

    assert valid is True
    assert form.cleaned_data == {
        'company_name': 'Amazon UK',
        'website': 'http://amazon.co.uk',
        'description': 'Ecommerce',
        'logo': logo,
    }


def test_company_profile_rejects_too_large_logo():
    logo = create_file_of_size(settings.MAX_LOGO_SIZE_BYTES + 1)
    form = forms.CompanyBasicInfoForm(data={}, files={'logo': logo})

    assert form.is_valid() is False
    assert form.errors['logo'] == [validators.MESSAGE_FILE_TOO_BIG]


def test_company_profile_accepty_good_sized_logo():
    logo = create_file_of_size(settings.MAX_LOGO_SIZE_BYTES)
    form = forms.CompanyBasicInfoForm(data={}, files={'logo': logo})

    form.is_valid()
    assert 'logo' not in form.errors


def test_serialize_registration_forms():
    actual = forms.serialize_registration_forms({
        'aim_one': constants.AIMS[0][0],
        'aim_two': constants.AIMS[1][0],
        'company_number': '01234567',
        'email': 'contact@example.com',
        'name': 'jim',
        'password': 'hunter2',
        'referrer': 'google'
    })
    expected = {
        'aims': [constants.AIMS[0][0], constants.AIMS[1][0]],
        'company_number': '01234567',
        'email': 'contact@example.com',
        'personal_name': 'jim',
        'password': 'hunter2',
        'referrer': 'google'
    }
    assert actual == expected
