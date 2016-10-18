from directory_validators import enrolment

from user import forms


def test_serialize_user_profile_forms():
    actual = forms.serialize_user_profile_forms({
        'name': 'John Test.',
        'email': 'john@example.com',
    })
    expected = {
        'name': 'John Test.',
        'email': 'john@example.com',
    }
    assert actual == expected


def test_basic_user_form_validators():
    field = forms.UserBasicInfoForm.base_fields['email']
    assert enrolment.email_domain_free in field.validators
    assert enrolment.email_domain_disposable in field.validators
