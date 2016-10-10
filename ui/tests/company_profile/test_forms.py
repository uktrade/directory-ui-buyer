from ui import constants, forms


def test_company_profile_form_requires_name():
    form = forms.CompanyProfileForm(data={})

    valid = form.is_valid()

    assert valid is False
    assert 'company_name' in form.errors
    assert len(form.errors['company_name']) == 1
    assert form.errors['company_name'][0] == 'This field is required.'


def test_company_profile_form_requires_description():
    form = forms.CompanyProfileForm(data={})

    valid = form.is_valid()

    assert valid is False
    assert 'description' in form.errors
    assert len(form.errors['description']) == 1
    assert form.errors['description'][0] == 'This field is required.'


def test_company_profile_form_requires_website():
    form = forms.CompanyProfileForm(data={})

    valid = form.is_valid()

    assert valid is False
    assert 'website' in form.errors
    assert len(form.errors['website']) == 1
    assert form.errors['website'][0] == 'This field is required.'


def test_company_profile_form_rejects_invalid_website():
    form = forms.CompanyProfileForm(data={'website': 'google'})

    valid = form.is_valid()

    assert valid is False
    assert 'website' in form.errors
    assert len(form.errors['website']) == 1
    assert form.errors['website'][0] == 'Enter a valid URL.'


def test_company_profile_form_accepts_valid_data():
    data = {'company_name': 'Amazon UK',
            'website': 'http://amazon.co.uk',
            'description': 'Ecommerce'}
    form = forms.CompanyProfileForm(data=data)

    valid = form.is_valid()

    assert valid is True
