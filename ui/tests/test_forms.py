from ui import forms


def test_step_one_rejects_missing_data():
    form = forms.RegisterStepOne(data={})
    assert form.is_valid() is False
    assert 'company_number' in form.errors
    assert 'company_email' in form.errors
    assert 'company_email_confirmed' in form.errors


def test_step_one_rejects_different_emails():
    form = forms.RegisterStepOne(data={
        'company_email': 'me@bagels4U.com',
        'company_email_confirmed': 'me@bagels4U.cm',
    })
    assert form.is_valid() is False
    assert 'company_email_confirmed' in form.errors


def test_step_one_accepts_valid_data():
    form = forms.RegisterStepOne(data={
        'company_number': 12456,
        'company_email': 'me@bagels4U.com',
        'company_email_confirmed': 'me@bagels4U.com',
        'terms_agreed': True,
    })
    assert form.is_valid() is True



def test_step_one_rejects_non_agreed_terms():
    form = forms.RegisterStepOne(data={
        'terms_agreed': ''
    })
    assert form.is_valid() is False
    assert 'terms_agreed' in form.errors


def test_step_two_rejects_missing_data():
    form = forms.RegisterStepTwo(data={})
    assert form.is_valid() is False
    expected = [
        'password',
        'password_confirmed',
    ]
    for key in expected:
        assert key in form.errors


def test_step_two_accepts_valid_data():
    form = forms.RegisterStepTwo(data={
        'password': 'password',
        'password_confirmed': 'password',
    })
    assert form.is_valid()


def test_step_two_rejects_different_passwords():
    form = forms.RegisterStepTwo(data={
        'password': 'password',
        'password_confirmed': 'pasword',
    })
    assert form.is_valid() is False
    assert 'password_confirmed' in form.errors

