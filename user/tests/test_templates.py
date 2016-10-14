from django.template.loader import render_to_string

user_context = {
    'user': {
        'name': 'Jim Fredson',
        'email': 'email@example.com',
    }
}


def test_user_profile_details_renders_name():
    html = render_to_string('user-profile-details.html', user_context)
    assert 'Jim Fredson' in html


def test_user_profile_details_renders_email():
    html = render_to_string('user-profile-details.html', user_context)
    assert 'email@example.com' in html


def test_user_profile_details_handles_no_email_or_mobile():
    html = render_to_string('user-profile-details.html', {})
    assert html.count('Unknown') == 2
