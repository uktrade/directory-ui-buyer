from directory_validators.enrolment import MESSAGE_INVALID_PHONE_NUMBER

from django import forms

from enrolment import fields

REQUIRED_MESSAGE = fields.PaddedCharField.default_error_messages['required']


class PaddedTestForm(forms.Form):
    field = fields.PaddedCharField(fillchar='0', max_length=6)


class MobilePhoneNumberTestForm(forms.Form):
    field = fields.MobilePhoneNumberField()


def test_padded_field_padds_value():
    form = PaddedTestForm(data={'field': 'val'})

    assert form.is_valid()
    assert form.cleaned_data['field'] == '000val'


def test_padded_field_handles_empty():
    for value in ['', None]:
        form = PaddedTestForm(data={'field': value})

        assert form.is_valid() is False
        assert form.errors['field'] == [REQUIRED_MESSAGE]


def test_mobile_phone_number_handles_empty():
    for value in ['', None]:
        form = MobilePhoneNumberTestForm(data={'field': value})

        assert form.is_valid() is False
        assert form.errors['field'] == [REQUIRED_MESSAGE]


def test_mobile_phone_number_handles_validation():
    form = MobilePhoneNumberTestForm(data={'field': '0750674388'})

    assert form.is_valid() is False
    assert form.errors['field'] == [MESSAGE_INVALID_PHONE_NUMBER]


def test_mobile_phone_number_handles_spaces():
    form = MobilePhoneNumberTestForm(data={'field': '0 75067 438 88 '})

    assert form.is_valid() is True
    assert form.cleaned_data['field'] == '07506743888'


def test_mobile_phone_number_handles_country_code():
    form = MobilePhoneNumberTestForm(data={'field': '+4475067 438 88'})

    assert form.is_valid() is True
    assert form.cleaned_data['field'] == '07506743888'
