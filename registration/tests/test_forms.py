from registration import constants, forms


def test_step_one_rejects_missing_data():
    form = forms.CompanyForm(data={})
    assert form.is_valid() is False
    assert 'company_number' in form.errors


def test_step_one_rejects_too_long_company_number():
    form = forms.CompanyForm(data={
        'company_number': '012456789',
    })
    assert form.is_valid() is False
    assert 'company_number' in form.errors


def test_step_one_rejects_too_short_company_number():
    form = forms.CompanyForm(data={
        'company_number': '0124567',
    })
    assert form.is_valid() is False
    assert 'company_number' in form.errors


def test_step_one_accepts_valid_data():
    form = forms.CompanyForm(data={
        'company_number': '01245678',
    })
    assert form.is_valid() is True


def test_step_two_accepts_valid_data():
    form = forms.AimsForm(data={
        'aim_one': constants.AIMS[1][0],
        'aim_two': constants.AIMS[2][0],
    })
    assert form.is_valid()


def test_step_two_rejects_no_aims():
    form = forms.AimsForm(data={
        'aim_one': '',
        'aim_two': '',
    })
    assert form.is_valid() is False


def test_step_three_rejects_missing_data():
    form = forms.UserForm(data={})
    assert 'name' in form.errors
    assert 'password' in form.errors
    assert 'terms_agreed' in form.errors
    assert 'email' in form.errors


def test_step_three_rejects_invalid_email_addresses():
    form = forms.UserForm(data={
        'email': 'johnATjones.com',
    })
    assert form.is_valid() is False
    assert 'email' in form.errors


def test_step_three_accepts_valid_data():
    form = forms.UserForm(data={
        'name': 'John Johnson',
        'password': 'hunter2',
        'terms_agreed': 1,
        'email': 'john@jones.com',
    })
    assert form.is_valid()


def test_company_profile_form_requires_name():
    form = forms.CompanyBasicInfoForm(data={})

    valid = form.is_valid()

    assert valid is False
    assert 'company_name' in form.errors
    assert len(form.errors['company_name']) == 1
    assert form.errors['company_name'][0] == 'This field is required.'


def test_company_profile_form_requires_description():
    form = forms.CompanyBasicInfoForm(data={})

    valid = form.is_valid()

    assert valid is False
    assert 'description' in form.errors
    assert len(form.errors['description']) == 1
    assert form.errors['description'][0] == 'This field is required.'


def test_company_profile_form_requires_website():
    form = forms.CompanyBasicInfoForm(data={})

    valid = form.is_valid()

    assert valid is False
    assert 'website' in form.errors
    assert len(form.errors['website']) == 1
    assert form.errors['website'][0] == 'This field is required.'


def test_company_profile_form_rejects_invalid_website():
    form = forms.CompanyBasicInfoForm(data={'website': 'google'})

    valid = form.is_valid()

    assert valid is False
    assert 'website' in form.errors
    assert len(form.errors['website']) == 1
    assert form.errors['website'][0] == 'Enter a valid URL.'


def test_company_profile_form_accepts_valid_data():
    data = {'company_name': 'Amazon UK',
            'website': 'http://amazon.co.uk',
            'description': 'Ecommerce'}
    form = forms.CompanyBasicInfoForm(data=data)

    valid = form.is_valid()

    assert valid is True
