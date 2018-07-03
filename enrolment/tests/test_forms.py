from unittest.mock import Mock, patch

from directory_components.fields import PaddedCharField
from directory_validators.company import no_html
import pytest

from django.forms import Form, HiddenInput
from django.forms.fields import CharField, Field
from django.core.validators import EmailValidator

from enrolment import forms, validators


REQUIRED_MESSAGE = Field.default_error_messages['required']
EMAIL_FORMAT_MESSAGE = EmailValidator.message


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
        forms.CompanyExportStatusForm,
    ]
    for FormClass in FormClasses:
        assert issubclass(FormClass, forms.AutoFocusFieldMixin)


def test_indent_invalid_mixin_installed():
    FormClasses = [
        forms.CompanyForm,
        forms.CompanyExportStatusForm,
    ]
    for FormClass in FormClasses:
        assert issubclass(FormClass, forms.IndentedInvalidFieldsMixin)


@patch.object(validators, 'company_unique', Mock())
def test_company_form_rejects_missing_data():
    form = forms.CompanyForm(data={})
    assert form.is_valid() is False
    assert form.errors['company_number'] == [REQUIRED_MESSAGE]


def test_company_form_fields():
    field = forms.CompanyForm.base_fields['company_number']

    assert isinstance(field, PaddedCharField)
    assert field.max_length == 8
    assert field.fillchar == '0'


def test_company_export_status_has_exported():
    form = forms.CompanyExportStatusForm(data={
        'has_exported_before': 'True',
        'terms_agreed': True,
    })

    assert form.is_valid() is True
    assert form.cleaned_data['has_exported_before'] is True


def test_company_export_status_not_exported():
    form = forms.CompanyExportStatusForm(data={
        'has_exported_before': 'False',
        'terms_agreed': True,
    })

    assert form.is_valid() is True
    assert form.cleaned_data['has_exported_before'] is False


def test_get_company_name_form_initial_data():
    actual = forms.get_company_form_initial_data(
        data={
            'company_name': 'Example',
            'company_number': 1234,
            'registered_office_address': {
                'address_line_1': 'address_line_1',
                'address_line_2': 'address_line_2',
                'care_of': 'care_of',
                'country': 'country',
                'locality': 'locality',
                'po_box': 'po_box',
                'postal_code': 'postal_code',
                'premises': 'premises',
                'region': 'region'
            }
        }
    )
    expected = {
        'company_name': 'Example',
        'company_number': 1234,
        'company_address': (
            'address_line_1, address_line_2, care_of, country, '
            'locality, po_box, postal_code, premises, region'
        )
    }
    assert actual == expected


@pytest.mark.parametrize('field', [
    forms.CompanyForm().fields['company_name'],
    forms.CompanyForm().fields['company_address'],
])
def test_xss_attack(field):
    assert no_html in field.validators
