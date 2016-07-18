from django import forms


class ContactForm(forms.Form):
    company_name = forms.CharField(required=True, max_length=255)
    contact_name = forms.CharField(required=True, max_length=255)
    email_address1 = forms.EmailField(required=True, max_length=255)
    email_address2 = forms.EmailField(required=True, max_length=255)
    mobile_number = forms.CharField(required=False, max_length=255)
    office_number = forms.CharField(required=False, max_length=255)
    website = forms.CharField(required=False, max_length=255)
    address1 = forms.CharField(required=True, max_length=255)
    address2 = forms.CharField(required=False, max_length=255)
    town_or_city = forms.CharField(required=True, max_length=255)
    county = forms.CharField(required=False, max_length=255)
    postcode = forms.CharField(required=True, max_length=255)
    exporting = forms.ChoiceField(
        required=True,
        choices=[('True', 'True'), ('False', 'False')],
        widget=forms.RadioSelect(),
    )
