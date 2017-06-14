from unittest.mock import Mock, patch

from django.forms import Form, HiddenInput
from django.forms.fields import CharField, Field
from django.core.validators import EmailValidator

from directory_validators import enrolment as shared_validators

from enrolment import fields, forms, validators, widgets


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

    assert isinstance(field, fields.PaddedCharField)
    assert field.max_length == 8
    assert field.fillchar == '0'


def test_company_export_status_form_validars():
    field = forms.CompanyExportStatusForm.base_fields['export_status']
    validator = shared_validators.export_status_intention
    assert validator in field.validators


def test_company_export_status_terms_agreed_checlbox_widget():
    field = forms.CompanyExportStatusForm().fields['terms_agreed']

    assert isinstance(field.widget, widgets.CheckboxWithInlineLabel)


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
