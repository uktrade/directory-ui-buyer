from unittest.mock import Mock, patch

from directory_validators import enrolment as shared_validators

from enrolment import forms, validators


def create_mock_file():
    return Mock(size=1)


@patch.object(validators, 'company_number', Mock())
def test_company_form_rejects_missing_data():
    form = forms.CompanyForm(data={})
    assert form.is_valid() is False
    assert 'company_number' in form.errors


def test_company_form_validators():
    field = forms.CompanyForm.base_fields['company_number']
    inner_validators = field.validators[0].inner_validators
    assert shared_validators.company_number in inner_validators
    assert validators.company_number in inner_validators


def test_company_email_form_email_validators():
    field = forms.CompanyEmailAddressForm.base_fields['company_email']
    assert shared_validators.email_domain_free in field.validators
    assert shared_validators.email_domain_disposable in field.validators


def test_company_email_form_rejects_invalid_email_addresses():
    form = forms.CompanyEmailAddressForm(data={
        'company_email': 'johnATjones.com',
    })
    assert form.is_valid() is False
    assert 'company_email' in form.errors


def test_test_company_email_form_rejects_different_email_addresses():
    form = forms.CompanyEmailAddressForm(data={
        'company_email': 'john@examplecorp.com',
        'email_confirmed': 'john@examplecorp.cm',
    })
    assert form.is_valid() is False
    assert 'email_confirmed' in form.errors


def test_test_user_form_rejects_different_mobile_numbers():
    form = forms.UserForm(data={
        'mobile_number': '111',
        'mobile_confirmed': '112',
    })
    assert form.is_valid() is False
    assert 'mobile_confirmed' in form.errors


def test_user_form_rejects_missing_data():
    form = forms.UserForm(data={})
    assert 'mobile_number' in form.errors
    assert 'mobile_confirmed' in form.errors
    assert 'mobile_confirmed' in form.errors
    assert 'terms_agreed' in form.errors


def test_user_form_accepts_valid_data():
    form = forms.UserForm(data={
        'mobile_number': '07506674933',
        'mobile_confirmed': '07506674933',
        'terms_agreed': 1,
    })
    assert form.is_valid()


def test_company_profile_form_requires_name():
    form = forms.CompanyBasicInfoForm(data={})

    valid = form.is_valid()

    assert valid is False
    assert 'company_name' in form.errors
    assert len(form.errors['company_name']) == 1
    assert form.errors['company_name'][0] == 'This field is required.'


def test_company_profile_form_requires_keywords():
    form = forms.CompanyBasicInfoForm(data={})

    valid = form.is_valid()

    assert valid is False
    assert 'keywords' in form.errors
    assert len(form.errors['keywords']) == 1
    assert form.errors['keywords'][0] == 'This field is required.'


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
    data = {'company_name': 'Amazon UK',
            'website': 'http://amazon.co.uk',
            'keywords': 'Ecommerce'}
    form = forms.CompanyBasicInfoForm(data=data)

    valid = form.is_valid()

    assert valid is True
    assert form.cleaned_data == {
        'company_name': 'Amazon UK',
        'website': 'http://amazon.co.uk',
        'keywords': 'Ecommerce',
    }


def test_company_logo_form_accepts_valid_data():
    logo = create_mock_file()
    form = forms.CompanyLogoForm(files={'logo': logo})

    valid = form.is_valid()

    assert valid is True
    assert form.cleaned_data == {
        'logo': logo,
    }


def test_company_profile_logo_validator():
    field = forms.CompanyLogoForm.base_fields['logo']
    assert shared_validators.logo_filesize in field.validators


def test_company_export_status_form_validars():
    field = forms.CompanyExportStatusForm.base_fields['export_status']
    assert shared_validators.export_status_intention in field.validators


def test_company_description_form_accepts_valid_data():
    form = forms.CompanyDescriptionForm(data={
        'description': 'thing'
    })
    assert form.is_valid() is True
    assert form.cleaned_data['description'] == 'thing'


def test_company_description_form_rejects_invalid_data():
    form = forms.CompanyDescriptionForm(data={})
    assert form.is_valid() is False
    assert form.errors['description'] == ['This field is required.']


def test_phone_number_verification_form_rejects_missing_data():
    form = forms.PhoneNumberVerificationForm(expected_sms_code=123, data={})
    assert form.is_valid() is False
    assert form.errors['sms_code'] == ['This field is required.']


def test_phone_number_verification_form_accepts_valid_data():
    expected_sms_code = '123'
    data = {
        'sms_code': expected_sms_code,
    }
    form = forms.PhoneNumberVerificationForm(
        expected_sms_code=expected_sms_code, data=data
    )
    assert form.is_valid() is True


def test_phone_number_verification_form_rejects_invalid_data():
    data = {
        'sms_code': 567,
    }
    form = forms.PhoneNumberVerificationForm(expected_sms_code=123, data=data)
    assert form.is_valid() is False
    assert form.errors['sms_code'] == ['Incorrect code.']


def test_serialize_enrolment_forms():
    actual = forms.serialize_enrolment_forms({
        'company_name': 'Extreme Corp',
        'company_number': '01234567',
        'mobile_number': '07504738222',
        'company_email': 'contact@example.com',
        'export_status': 'YES',
        'referrer': 'google'
    })
    expected = {
        'company_name': 'Extreme Corp',
        'company_number': '01234567',
        'mobile_number': '07504738222',
        'company_email': 'contact@example.com',
        'export_status': 'YES',
        'referrer': 'google'
    }
    assert actual == expected


def test_serialize_company_profile_forms():
    actual = forms.serialize_company_profile_forms({
        'company_name': 'Example ltd.',
        'keywords': 'Jolly good exporter.',
        'employees': '1-10',
        'sectors': ['1', '2'],
        'website': 'http://example.com',
    })
    expected = {
        'keywords': 'Jolly good exporter.',
        'employees': '1-10',
        'name': 'Example ltd.',
        'sectors': ['1', '2'],
        'website': 'http://example.com',
    }
    assert actual == expected


def test_serialize_company_logo_forms():
    logo = create_mock_file()
    actual = forms.serialize_company_logo_forms({
        'logo': logo,
    })
    expected = {
        'logo': logo,
    }
    assert actual == expected


def test_serialize_company_description_forms():
    actual = forms.serialize_company_description_forms({
        'description': 'Jolly good exporter.',
    })
    expected = {
        'description': 'Jolly good exporter.',
    }
    assert actual == expected
