from django import forms


class ContactForm(forms.Form):
    company_name = forms.CharField(required=True, max_length=255)
    contact_name = forms.CharField(required=True, max_length=255)
    email_address1 = forms.EmailField(required=True, max_length=255)
    email_address2 = forms.EmailField(required=True, max_length=255)
    phone_number = forms.CharField(required=False, max_length=255)
    website = forms.CharField(required=False, max_length=255)
    exporting = forms.ChoiceField(
        required=True,
        choices=[('True', 'True'), ('False', 'False')],
        widget=forms.RadioSelect(),
    )
    agree_terms = forms.BooleanField(required=True)
    opt_in = forms.BooleanField(required=False)

    # def clean(self):
    #     cleaned_data = super().clean()
    #     email1 = cleaned_data.get("email_address1")
    #     email2 = cleaned_data.get("email_address2")

    #     if email1 and email2 and email1 != email2:
    #         raise forms.ValidationError("Emails do not match.")

    #     return cleaned_data
