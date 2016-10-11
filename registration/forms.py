from django import forms

from registration import constants


class CompanyForm(forms.Form):
    company_number = forms.CharField(
        label='Company number',
        help_text=('This is the 8-digit number on the company certificate of '
                   'incorporation.'),
        max_length=8,
        min_length=8,
    )


class CompanyBasicInfoForm(forms.Form):
    company_name = forms.CharField()
    website = forms.URLField()
    description = forms.CharField(widget=forms.Textarea)


class AimsForm(forms.Form):
    aim_one = forms.ChoiceField(choices=constants.AIMS)
    aim_two = forms.ChoiceField(choices=constants.AIMS)


class UserForm(forms.Form):
    name = forms.CharField(label='Full name')
    email = forms.EmailField(label='Email address')
    password = forms.CharField(widget=forms.PasswordInput())
    terms_agreed = forms.BooleanField()
    referrer = forms.CharField(required=False, widget=forms.HiddenInput())
