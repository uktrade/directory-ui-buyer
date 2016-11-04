from unittest.mock import Mock, patch

from directory_validators import enrolment as shared_validators

from django.forms.fields import Field
from django.core.validators import EmailValidator, URLValidator

from enrolment import forms, validators


REQUIRED_MESSAGE = Field.default_error_messages['required']
EMAIL_FORMAT_MESSAGE = EmailValidator.message
URL_FORMAT_MESSAGE = URLValidator.message


def create_mock_file():
    return Mock(size=1)


@patch.object(validators, 'company_number', Mock())
def test_company_form_rejects_missing_data():
    form = forms.CompanyForm(data={})
    assert form.is_valid() is False
    assert form.errors['company_number'] == [REQUIRED_MESSAGE]


def test_company_form_validators():
    field = forms.CompanyForm.base_fields['company_number']
    inner_validators = field.validators[0].inner_validators
    assert shared_validators.company_number in inner_validators
    assert validators.company_number in inner_validators


def test_company_email_form_email_validators():
    field = forms.CompanyEmailAddressForm.base_fields['company_email']
    inner_validators = field.validators[1].inner_validators
    assert shared_validators.email_domain_free in inner_validators
    assert shared_validators.email_domain_disposable in inner_validators
    assert validators.email_address in inner_validators


@patch('enrolment.validators.api_client', Mock())
def test_company_email_form_rejects_invalid_email_addresses():
    form = forms.CompanyEmailAddressForm(data={
        'company_email': 'johnATjones.com',
    })

    assert form.is_valid() is False
    assert form.errors['company_email'] == [EMAIL_FORMAT_MESSAGE]


@patch('enrolment.validators.api_client', Mock())
def test_test_company_email_form_rejects_different_email_addresses():
    form = forms.CompanyEmailAddressForm(data={
        'company_email': 'john@examplecorp.com',
        'email_confirmed': 'john@examplecorp.cm',
    })
    expected = forms.CompanyEmailAddressForm.error_messages['different']

    assert form.is_valid() is False
    assert form.errors['email_confirmed'] == [expected]


def test_test_user_form_rejects_different_mobile_numbers():
    form = forms.UserForm(data={
        'mobile_number': '111',
        'mobile_confirmed': '112',
    })
    expected = forms.UserForm.error_messages['different']

    assert form.is_valid() is False
    assert form.errors['mobile_confirmed'] == [expected]


def test_user_form_rejects_missing_data():
    form = forms.UserForm(data={})

    assert form.is_valid() is False
    assert form.errors['mobile_number'] == [REQUIRED_MESSAGE]
    assert form.errors['mobile_confirmed'] == [REQUIRED_MESSAGE]
    assert form.errors['terms_agreed'] == [REQUIRED_MESSAGE]


def test_user_form_accepts_valid_data():
    form = forms.UserForm(data={
        'mobile_number': '07506674933',
        'mobile_confirmed': '07506674933',
        'terms_agreed': 1,
    })
    assert form.is_valid()


def test_international_form_missing_data():
    form = forms.InternationalBuyerForm(data={})

    assert form.is_valid() is False
    assert form.errors['full_name'] == [REQUIRED_MESSAGE]
    assert form.errors['email_address'] == [REQUIRED_MESSAGE]
    assert form.errors['sector'] == [REQUIRED_MESSAGE]
    assert form.errors['terms'] == [REQUIRED_MESSAGE]


def test_international_form_accepts_valid_data():
    form = forms.InternationalBuyerForm(data={
        'full_name': 'Jim Example',
        'email_address': 'jim@example.com',
        'sector': 'AEROSPACE',
        'terms': True
    })
    assert form.is_valid()


def test_company_profile_form_required_fields():
    form = forms.CompanyBasicInfoForm(data={})

    valid = form.is_valid()

    assert valid is False
    assert form.errors['company_name'] == [REQUIRED_MESSAGE]
    assert form.errors['website'] == [REQUIRED_MESSAGE]
    assert form.errors['keywords'] == [REQUIRED_MESSAGE]


def test_company_profile_form_url_validator():
    field = forms.CompanyBasicInfoForm.base_fields['website']
    assert isinstance(field.validators[0], URLValidator)


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
    assert form.errors['description'] == [REQUIRED_MESSAGE]


def test_phone_number_verification_form_rejects_missing_data():
    form = forms.PhoneNumberVerificationForm(expected_sms_code=123, data={})
    assert form.is_valid() is False
    assert form.errors['sms_code'] == [REQUIRED_MESSAGE]


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
    expected = forms.PhoneNumberVerificationForm.error_messages['different']

    assert form.is_valid() is False
    assert form.errors['sms_code'] == [expected]


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
        'sectors': '["1", "2"]',
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
