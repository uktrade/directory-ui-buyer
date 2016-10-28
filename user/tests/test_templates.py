from django.template.loader import render_to_string

user_context = {
    'user': {
        'company_email': 'email@example.com',
        'company_id': '01234567',
        'mobile_number': '02343543333',
    }
}


def test_user_profile_details_renders_phone_number():
    html = render_to_string('user-profile-details.html', user_context)
    assert '02343543333' in html


def test_user_profile_details_renders_company_number():
    html = render_to_string('user-profile-details.html', user_context)
    assert '01234567' in html


def test_user_profile_details_renders_email():
    html = render_to_string('user-profile-details.html', user_context)
    assert 'email@example.com' in html
