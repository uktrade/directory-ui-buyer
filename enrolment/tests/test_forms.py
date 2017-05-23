import http
from unittest.mock import Mock, patch

from directory_validators import enrolment as shared_validators
from requests.exceptions import RequestException

from django.forms import Form, HiddenInput

from django.forms.fields import CharField, Field
from django.core.validators import EmailValidator

from enrolment import fields, forms, helpers, validators


REQUIRED_MESSAGE = Field.default_error_messages['required']
EMAIL_FORMAT_MESSAGE = EmailValidator.message
TERMS_CONDITIONS_MESSAGE = \
    forms.InternationalBuyerForm.TERMS_CONDITIONS_MESSAGE


class FormWithAutoFocusFieldMixin(forms.AutoFocusFieldMixin, Form):
    hiddenfield = CharField(widget=HiddenInput())
    field1 = CharField()
    field1 = CharField()


def auto_focus_field_autofocus():
    form = FormWithAutoFocusFieldMixin()
    assert form.fields['field1'].widget.attrs['autofocus'] == 'autofocus'
    assert form.fields['field2'].widget.attrs == {}


def test_auto_focus_mixin_installed():
    FormClasses = [
        forms.CompanyForm,
        forms.CompanyForm,
        forms.CompanyExportStatusForm,
    ]
    for FormClass in FormClasses:
        assert issubclass(FormClass, forms.AutoFocusFieldMixin)


def test_indent_invalid_mixin_installed():
    FormClasses = [
        forms.CompanyForm,
        forms.CompanyForm,
        forms.CompanyExportStatusForm,
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
    data = {
        'company_number': '01234567',
        'terms_agreed': True,
    }

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
    data = {
        'company_number': '01234567',
        'terms_agreed': True,
    }

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
    data = {
        'company_number': '01234567',
        'terms_agreed': True,
    }

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
    data = {
        'company_number': '01234567',
        'terms_agreed': True,
    }

    form = forms.CompanyForm(data=data, session=session)

    assert form.is_valid() is True

    mock_company_active.assert_called_once_with('active')


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


def test_serialize_enrolment_forms():
    actual = forms.serialize_enrolment_forms({
        'company_number': '01234567',
        'export_status': 'YES',
    })
    expected = {
        'company_number': '01234567',
        'export_status': 'YES',
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
