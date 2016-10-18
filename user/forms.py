from django import forms

from directory_validators import enrolment as validators


class UserBasicInfoForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField(
        validators=[
            validators.email_domain_free,
            validators.email_domain_disposable,
        ]
    )


def serialize_user_profile_forms(cleaned_data):
    """
    Return the shape directory-api-client expects for user profile update.

    @param {dict} cleaned_data - All the fields in `UserBasicInfoForm`
    @returns dict

    """

    return {
        'name': cleaned_data['name'],
        'email': cleaned_data['email'],
    }
