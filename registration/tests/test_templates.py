from django.template.loader import render_to_string

company_context = {
    'company': {
        'aims': [
            'aim 1',
            'aim 2'
        ],
        'number': '123456',
        'name': 'UK exporting co ltd.',
        'description': 'Exporters of UK wares.',
        'website': 'www.ukexportersnow.co.uk',
        'logo': 'www.ukexportersnow.co.uk/logo.png',
    }
}

user_context = {
    'user': {
        'mobile': '00000000011',
        'email': 'email@example.com',
    }
}


def test_company_profile_details_renders_aims():
    html = render_to_string('company-profile-details.html', company_context)
    assert 'aim 1' in html
    assert 'aim 2' in html


def test_company_profile_details_renders_company_number():
    html = render_to_string('company-profile-details.html', company_context)
    assert '123456' in html


def test_company_profile_details_renders_company_name():
    html = render_to_string('company-profile-details.html', company_context)
    assert 'Company profile - UK exporting co ltd.' in html


def test_company_profile_details_renders_description():
    html = render_to_string('company-profile-details.html', company_context)
    assert 'Exporters of UK wares.' in html


def test_company_profile_details_renders_website():
    html = render_to_string('company-profile-details.html', company_context)
    assert 'www.ukexportersnow.co.uk' in html


def test_company_profile_details_renders_logo():
    html = render_to_string('company-profile-details.html', company_context)
    assert 'www.ukexportersnow.co.uk/logo.png' in html


def test_company_profile_details_handles_no_description():
    html = render_to_string('company-profile-details.html', {})
    assert 'Please set your company description.' in html


def test_company_profile_details_handles_no_company_name():
    html = render_to_string('company-profile-details.html', {})
    assert 'Company profile -' not in html
    assert 'Company profile' in html


def test_company_profile_details_handles_no_website():
    html = render_to_string('company-profile-details.html', {})
    assert 'Please set your website address.' in html


def test_user_profile_details_renders_mobile():
    html = render_to_string('user-profile-details.html', user_context)
    assert '00000000011' in html


def test_user_profile_details_renders_email():
    html = render_to_string('user-profile-details.html', user_context)
    assert 'email@example.com' in html


def test_user_profile_details_handles_no_email_or_mobile():
    html = render_to_string('user-profile-details.html', {})
    assert html.count('Unknown') == 2
