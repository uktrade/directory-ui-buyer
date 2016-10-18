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
