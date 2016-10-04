from django import forms
from django.forms.utils import ErrorList


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


class RegisterStepOne(forms.Form):
    company_number = forms.CharField(label='Company number')
    company_email = forms.EmailField()
    company_email_confirmed = forms.EmailField()
    terms_agreed = forms.BooleanField()

    def clean_company_email_confirmed(self):
        email = self.cleaned_data.get('company_email')
        email_confirmed = self.cleaned_data.get('company_email_confirmed')
        if email and email != email_confirmed:
            raise forms.ValidationError('Your emails must match')
        return email_confirmed


class RegisterStepTwo(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput())
    password_confirmed = forms.CharField(widget=forms.PasswordInput())

    def clean_password_confirmed(self):
        password = self.cleaned_data.get('password')
        password_confirmed = self.cleaned_data.get('password_confirmed')
        if password and password != password_confirmed:
            raise forms.ValidationError('Your passwords must match')
        return password_confirmed
