from unittest.mock import Mock, patch

from directory_validators import company as shared_company_validators
from directory_validators import enrolment as shared_enrolment_validators

from django.forms import Form
from django.forms.fields import CharField, Field
from django.core.validators import EmailValidator, URLValidator
from django.core.urlresolvers import reverse

from enrolment import fields, forms, helpers, validators, views


REQUIRED_MESSAGE = Field.default_error_messages['required']
EMAIL_FORMAT_MESSAGE = EmailValidator.message
URL_FORMAT_MESSAGE = URLValidator.message
TERMS_CONDITIONS_MESSAGE = \
    forms.InternationalBuyerForm.TERMS_CONDITIONS_MESSAGE


class FormWithAutoFocusFieldMixin(forms.AutoFocusFieldMixin, Form):
    field1 = CharField()
    field1 = CharField()


def create_mock_file():
    return Mock(size=1)


def auto_focus_field_autofocus():
    form = FormWithAutoFocusFieldMixin()
    assert form.fields['field1'].widget.attrs['autofocus'] == 'autofocus'
    assert form.fields['field2'].widget.attrs == {}


def test_auto_focus_mixin_installed():
    FormClasses = [
        forms.CompanyNameForm,
        forms.CompanyForm,
        forms.CompanyExportStatusForm,
        forms.CompanyBasicInfoForm,
        forms.CompanyDescriptionForm,
        forms.CompanyLogoForm,
        forms.CompanyEmailAddressForm,
        forms.UserForm,
        forms.CompanySizeForm,
        forms.CompanyClassificationForm,
        forms.PhoneNumberVerificationForm,
        forms.InternationalBuyerForm,
    ]
    for FormClass in FormClasses:
        assert issubclass(FormClass, forms.AutoFocusFieldMixin)


def test_indent_invalid_mixin_installed():
    FormClasses = [
        forms.CompanyNameForm,
        forms.CompanyForm,
        forms.CompanyExportStatusForm,
        forms.CompanyBasicInfoForm,
        forms.CompanyDescriptionForm,
        forms.CompanyLogoForm,
        forms.CompanyEmailAddressForm,
        forms.UserForm,
        forms.CompanySizeForm,
        forms.CompanyClassificationForm,
        forms.PhoneNumberVerificationForm,
        forms.InternationalBuyerForm,
    ]
    for FormClass in FormClasses:
        assert issubclass(FormClass, forms.IndentedInvalidFieldsMixin)


@patch.object(validators, 'company_number', Mock())
def test_company_form_rejects_missing_data():
    form = forms.CompanyForm(data={})
    assert form.is_valid() is False
    assert form.errors['company_number'] == [REQUIRED_MESSAGE]


def test_company_form_fields():
    field = forms.CompanyForm.base_fields['company_number']

    assert isinstance(field, fields.PaddedCharField)
    assert field.max_length == 8
    assert field.fillchar == '0'


def test_user_form_fields():
    mobile_number_field = forms.UserForm.base_fields['mobile_number']
    mobile_confirmed_field = forms.UserForm.base_fields['mobile_confirmed']

    assert isinstance(mobile_number_field, fields.MobilePhoneNumberField)
    # we dont want both fields to be MobilePhoneNumberField - that would
    # result in validation inside the field's `to_python` firing before
    # clean_mobile_confirmed fires, meaning different mobile number in
    # mobile_confirmed could show 'invalid number' instead of 'not the same'.
    assert isinstance(mobile_confirmed_field, CharField)


def test_company_form_validators():
    field = forms.CompanyForm.base_fields['company_number']
    inner_validators = field.validators[0].inner_validators
    assert shared_enrolment_validators.company_number in inner_validators
    assert validators.company_number in inner_validators


def test_company_email_form_email_validators():
    field = forms.CompanyEmailAddressForm.base_fields['company_email']
    inner = field.validators[1].inner_validators
    assert shared_enrolment_validators.email_domain_free in inner
    assert shared_enrolment_validators.email_domain_disposable in inner
    assert validators.email_address in inner


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


@patch('enrolment.validators.api_client', Mock())
def test_test_user_form_rejects_different_mobile_numbers():
    form = forms.UserForm(data={
        'mobile_number': '07507605443',
        'mobile_confirmed': '07507605444',
    })
    expected = forms.UserForm.error_messages['different']

    assert form.is_valid() is False
    assert form.errors['mobile_confirmed'] == [expected]


@patch('enrolment.validators.api_client', Mock())
def test_user_form_rejects_missing_data():
    form = forms.UserForm(data={})

    assert form.is_valid() is False
    assert form.errors['mobile_number'] == [REQUIRED_MESSAGE]
    assert form.errors['mobile_confirmed'] == [REQUIRED_MESSAGE]
    assert form.errors['terms_agreed'] == [REQUIRED_MESSAGE]


@patch('enrolment.validators.api_client', Mock())
def test_user_form_accepts_valid_data():
    form = forms.UserForm(data={
        'mobile_number': '07506674933',
        'mobile_confirmed': '07506674933',
        'terms_agreed': 1,
    })
    assert form.is_valid()


@patch('enrolment.validators.api_client', Mock())
def test_user_form_validators():
    field = forms.UserForm.base_fields['mobile_number']
    inner_validators = field.validators[0].inner_validators
    assert validators.mobile_number in inner_validators


def test_international_form_missing_data():
    form = forms.InternationalBuyerForm(data={})

    assert form.is_valid() is False
    assert form.errors['full_name'] == [REQUIRED_MESSAGE]
    assert form.errors['email_address'] == [REQUIRED_MESSAGE]
    assert form.errors['sector'] == [REQUIRED_MESSAGE]
    assert form.errors['terms'] == [TERMS_CONDITIONS_MESSAGE]


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
    assert form.errors['name'] == [REQUIRED_MESSAGE]
    assert form.errors['website'] == [REQUIRED_MESSAGE]
    assert form.errors['keywords'] == [REQUIRED_MESSAGE]


def test_company_profile_form_keywords_validator():
    field = forms.CompanyBasicInfoForm.base_fields['keywords']
    assert shared_company_validators.keywords_word_limit in field.validators


def test_company_profile_form_url_validator():
    field = forms.CompanyBasicInfoForm.base_fields['website']
    assert isinstance(field.validators[0], URLValidator)


def test_company_profile_form_accepts_valid_data():
    data = {'name': 'Amazon UK',
            'website': 'http://amazon.co.uk',
            'keywords': 'Ecommerce'}
    form = forms.CompanyBasicInfoForm(data=data)

    valid = form.is_valid()

    assert valid is True
    assert form.cleaned_data == {
        'name': 'Amazon UK',
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


def test_company_logo_form_logo_is_required():
    form = forms.CompanyLogoForm(files={'logo': None})

    valid = form.is_valid()

    assert valid is False
    assert 'logo' in form.errors
    assert 'This field is required.' in form.errors['logo']


def test_company_profile_logo_validator():
    field = forms.CompanyLogoForm.base_fields['logo']
    assert shared_enrolment_validators.logo_filesize in field.validators


def test_company_export_status_form_validars():
    field = forms.CompanyExportStatusForm.base_fields['export_status']
    validator = shared_enrolment_validators.export_status_intention
    assert validator in field.validators


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


def test_phone_number_verification_form_help_text_links_to_register():
    field = forms.PhoneNumberVerificationForm.base_fields['sms_code']
    expected = reverse('register', kwargs={'step': views.EnrolmentView.USER})

    assert expected in field.help_text


def test_phone_number_verification_form_rejects_missing_data():
    form = forms.PhoneNumberVerificationForm(encoded_sms_code=123, data={})
    assert form.is_valid() is False
    assert form.errors['sms_code'] == [REQUIRED_MESSAGE]


def test_phone_number_verification_form_accepts_valid_data():
    encoded_sms_code = helpers.encrypt_sms_code('123')
    form = forms.PhoneNumberVerificationForm(
        encoded_sms_code=encoded_sms_code, data={'sms_code': '123'}
    )
    assert form.is_valid() is True


def test_phone_number_verification_form_rejects_invalid_data():
    data = {
        'sms_code': 567,
    }
    form = forms.PhoneNumberVerificationForm(encoded_sms_code=123, data=data)
    expected = forms.PhoneNumberVerificationForm.error_messages['different']

    assert form.is_valid() is False
    assert form.errors['sms_code'] == [expected]


def test_company_classification_form_sectors_validator():
    field = forms.CompanyClassificationForm.base_fields['sectors']
    assert shared_company_validators.sector_choice_limit in field.validators


def test_serialize_enrolment_forms():
    actual = forms.serialize_enrolment_forms({
        'name': 'Extreme Corp',
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
        'name': 'Example ltd.',
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


def test_serialize_international_buyer_forms():
    actual = forms.serialize_international_buyer_forms({
        'full_name': 'Jim Example',
        'email_address': 'jim@example.com',
        'sector': 'AEROSPACE',
    })
    expected = {
        'name': 'Jim Example',
        'email': 'jim@example.com',
        'sector': 'AEROSPACE',
    }
    assert actual == expected


def test_get_company_name_form_initial_data():
    actual = forms.get_company_name_form_initial_data(
        name='Example'
    )
    expected = {
        'name': 'Example'
    }
    assert actual == expected


def test_get_user_form_initial_data():
    actual = forms.get_user_form_initial_data(
        referrer='google'
    )
    expected = {
        'referrer': 'google'
    }
    assert actual == expected


def test_get_email_form_initial_data():
    actual = forms.get_email_form_initial_data(
        email='jerry@example.com',
    )
    expected = {
        'company_email': 'jerry@example.com',
        'email_confirmed': 'jerry@example.com',
    }

    assert actual == expected
