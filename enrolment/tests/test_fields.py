from django import forms

from enrolment import fields

REQUIRED_MESSAGE = fields.PaddedCharField.default_error_messages['required']


class TestForm(forms.Form):
    field = fields.PaddedCharField(fillchar='0', max_length=6)


def test_padded_field_padds_value():
    form = TestForm(data={'field': 'val'})

    assert form.is_valid()
    assert form.cleaned_data['field'] == '000val'


def test_padded_field_handles_empty():
    for value in ['', None]:
        form = TestForm(data={'field': value})

        assert form.is_valid() is False
        assert form.errors['field'] == [REQUIRED_MESSAGE]
