import http
from unittest.mock import Mock, patch

from directory_validators import enrolment as shared_validators
from requests.exceptions import RequestException

from django.forms import Form

from django.forms.fields import CharField, Field
from django.core.validators import EmailValidator
from django.core.urlresolvers import reverse

from enrolment import fields, forms, helpers, validators, views


REQUIRED_MESSAGE = Field.default_error_messages['required']
EMAIL_FORMAT_MESSAGE = EmailValidator.message
TERMS_CONDITIONS_MESSAGE = \
    forms.InternationalBuyerForm.TERMS_CONDITIONS_MESSAGE


class FormWithAutoFocusFieldMixin(forms.AutoFocusFieldMixin, Form):
    field1 = CharField()
    field1 = CharField()


def auto_focus_field_autofocus():
    form = FormWithAutoFocusFieldMixin()
    assert form.fields['field1'].widget.attrs['autofocus'] == 'autofocus'
    assert form.fields['field2'].widget.attrs == {}


def test_auto_focus_mixin_installed():
    FormClasses = [
        forms.CompanyNameForm,
        forms.CompanyForm,
        forms.CompanyExportStatusForm,
        forms.CompanyEmailAddressForm,
        forms.SupplierForm,
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
        forms.CompanyEmailAddressForm,
        forms.SupplierForm,
        forms.PhoneNumberVerificationForm,
        forms.InternationalBuyerForm,
    ]
    for FormClass in FormClasses:
        assert issubclass(FormClass, forms.IndentedInvalidFieldsMixin)


@patch.object(validators, 'company_unique', Mock())
def test_company_form_rejects_missing_data():
    form = forms.CompanyForm(data={}, session=Mock())
    assert form.is_valid() is False
    assert form.errors['company_number'] == [REQUIRED_MESSAGE]


def test_company_form_fields():
    field = forms.CompanyForm.base_fields['company_number']

    assert isinstance(field, fields.PaddedCharField)
    assert field.max_length == 8
    assert field.fillchar == '0'


def test_company_form_validators():
    field = forms.CompanyForm(data={}, session=Mock()).fields['company_number']
    inner_validators = field.validators[0].inner_validators
    assert shared_validators.company_number in inner_validators
    assert validators.company_unique in inner_validators


@patch.object(helpers, 'store_companies_house_profile_in_session')
@patch.object(validators, 'company_active', Mock())
@patch.object(helpers, 'get_company_status_from_session',
              Mock(return_value='active'))
def test_company_form_caches_profile(
    mock_store_companies_house_profile_in_session, client
):
    session = client.session
    data = {'company_number': '01234567'}

    form = forms.CompanyForm(data=data, session=session)

    assert form.is_valid() is True

    mock_store_companies_house_profile_in_session.assert_called_once_with(
        session=session,
        company_number=data['company_number'],
    )
    form.cleaned_data['company_number'] == data['company_number']


@patch.object(helpers, 'store_companies_house_profile_in_session')
@patch.object(validators, 'company_active', Mock())
def test_company_form_handles_api_company_not_found(
    mock_store_companies_house_profile_in_session, client
):
    exception = RequestException(
        response=Mock(status_code=http.client.NOT_FOUND),
        request=Mock(),
    )
    mock_store_companies_house_profile_in_session.side_effect = exception
    session = client.session
    data = {'company_number': '01234567'}

    form = forms.CompanyForm(data=data, session=session)

    assert form.is_valid() is False

    form.errors['company_number'] == [forms.MESSAGE_COMPANY_NOT_FOUND]


@patch.object(helpers, 'store_companies_house_profile_in_session')
@patch.object(validators, 'company_active', Mock())
def test_company_form_handles_api_error(
    mock_store_companies_house_profile_in_session, client
):
    exception = RequestException(
        response=Mock(status_code=http.client.INTERNAL_SERVER_ERROR),
        request=Mock(),
    )
    mock_store_companies_house_profile_in_session.side_effect = exception
    session = client.session
    data = {'company_number': '01234567'}

    form = forms.CompanyForm(data=data, session=session)

    assert form.is_valid() is False

    form.errors['company_number'] == [forms.MESSAGE_TRY_AGAIN_LATER]


@patch.object(helpers, 'store_companies_house_profile_in_session', Mock())
@patch.object(helpers, 'get_company_status_from_session',
              Mock(return_value='active'))
@patch.object(validators, 'company_active')
def test_company_form_handles_company_active_validation(
    mock_company_active, client
):
    session = client.session
    data = {'company_number': '01234567'}

    form = forms.CompanyForm(data=data, session=session)

    assert form.is_valid() is True

    mock_company_active.assert_called_once_with('active')


def test_supplier_form_fields():
    mobile_number_field = forms.SupplierForm.base_fields['mobile_number']
    mobile_confirmed_field = forms.SupplierForm.base_fields['mobile_confirmed']

    assert isinstance(mobile_number_field, fields.MobilePhoneNumberField)
    # we dont want both fields to be MobilePhoneNumberField - that would
    # result in validation inside the field's `to_python` firing before
    # clean_mobile_confirmed fires, meaning different mobile number in
    # mobile_confirmed could show 'invalid number' instead of 'not the same'.
    assert isinstance(mobile_confirmed_field, CharField)


def test_company_email_form_email_validators():
    field = forms.CompanyEmailAddressForm.base_fields['company_email']
    inner = field.validators[1].inner_validators
    assert shared_validators.email_domain_free in inner
    assert shared_validators.email_domain_disposable in inner
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
def test_test_supplier_form_rejects_different_mobile_numbers():
    form = forms.SupplierForm(data={
        'mobile_number': '07507605443',
        'mobile_confirmed': '07507605444',
    })
    expected = forms.SupplierForm.error_messages['different']

    assert form.is_valid() is False
    assert form.errors['mobile_confirmed'] == [expected]


@patch('enrolment.validators.api_client', Mock())
def test_supplier_form_rejects_missing_data():
    form = forms.SupplierForm(data={})

    assert form.is_valid() is False
    assert form.errors['mobile_number'] == [REQUIRED_MESSAGE]
    assert form.errors['mobile_confirmed'] == [REQUIRED_MESSAGE]
    assert form.errors['terms_agreed'] == [REQUIRED_MESSAGE]


@patch('enrolment.validators.api_client', Mock())
def test_supplier_form_accepts_valid_data():
    form = forms.SupplierForm(data={
        'mobile_number': '07506674933',
        'mobile_confirmed': '07506674933',
        'terms_agreed': 1,
    })
    assert form.is_valid()


@patch('enrolment.validators.api_client', Mock())
def test_supplier_form_accepts_valid_data_space_in_mobile_num():
    form = forms.SupplierForm(data={
        'mobile_number': '07506 674 933',
        'mobile_confirmed': '07506 674 933',
        'terms_agreed': 1,
    })
    assert form.is_valid()


@patch('enrolment.validators.api_client', Mock())
def test_supplier_form_validators():
    field = forms.SupplierForm.base_fields['mobile_number']
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


def test_company_export_status_form_validars():
    field = forms.CompanyExportStatusForm.base_fields['export_status']
    validator = shared_validators.export_status_intention
    assert validator in field.validators


def test_phone_number_verification_form_help_text_links_to_register():
    field = forms.PhoneNumberVerificationForm.base_fields['sms_code']
    expected = reverse(
        'register', kwargs={'step': views.EnrolmentView.SUPPLIER}
    )

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


def test_get_supplier_form_initial_data():
    actual = forms.get_supplier_form_initial_data(
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
