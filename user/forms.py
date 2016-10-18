from django import forms


class UserBasicInfoForm(forms.Form):
    name = forms.CharField()
    email = forms.URLField()
