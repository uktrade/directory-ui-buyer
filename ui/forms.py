from django import forms
from django.forms.utils import ErrorList

from ui import constants


class ContactForm(forms.Form):
    company_name = forms.CharField(required=True, max_length=255)
    contact_name = forms.CharField(required=True, max_length=255)
    email_address1 = forms.EmailField(required=True, max_length=255)
    email_address2 = forms.EmailField(required=True, max_length=255)
    phone_number = forms.CharField(required=False, max_length=255)
    website = forms.CharField(required=True, max_length=255)
    exporting = forms.ChoiceField(
        required=True,
        choices=[('True', 'True'), ('False', 'False')],
        widget=forms.RadioSelect(),
    )
    agree_terms = forms.BooleanField(required=True)
    opt_in = forms.BooleanField(required=False)

    marketing_source = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Please select an option'),
            ('Social media', 'Social media'),
            ('Print or online news', 'Print or online news'),
            ('Bank', 'Bank (please specify which bank, below)'),
            ('Department for International Trade', 'Department for International Trade'),
            ('HMRC email', 'HMRC email'),
            ('Exporting is GREAT website', 'Exporting is GREAT website'),
            ('Trade association', 'Trade association'),
            ('other', 'Other (please specify below)')
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    marketing_source_bank = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    marketing_source_other = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        email1 = cleaned_data.get("email_address1")
        email2 = cleaned_data.get("email_address2")

        if email1 and email2 and email1.lower() != email2.lower():
            for field in ['email_address1', 'email_address2']:
                if field not in self._errors:
                    self._errors[field] = ErrorList()
                self._errors[field].append(
                    'Email addresses do not match',
                )
        return cleaned_data


class CompanyForm(forms.Form):
    company_number = forms.CharField(
        label='Company number',
        help_text=('This is the 8-digit number on the company certificate of '
                   'incorporation.'),
        max_length=8,
        min_length=8,
    )


class AimsForm(forms.Form):
    aim_one = forms.ChoiceField(choices=constants.AIMS)
    aim_two = forms.ChoiceField(choices=constants.AIMS)


class UserForm(forms.Form):
    name = forms.CharField(label='Full name')
    email = forms.EmailField(label='Email address')
    password = forms.CharField(widget=forms.PasswordInput())
    terms_agreed = forms.BooleanField()
