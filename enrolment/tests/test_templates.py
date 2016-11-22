from django.template.loader import render_to_string

from directory_validators.constants import choices


from enrolment import forms

company_context = {
    'company': {
        'sectors': [
            'sector 1',
            'sector 2'
        ],
        'number': '123456',
        'name': 'UK exporting co ltd.',
        'description': 'Exporters of UK wares.',
        'website': 'www.ukexportersnow.co.uk',
        'logo': 'www.ukexportersnow.co.uk/logo.png',
        'keywords': 'word1 word2',
    }
}

user_context = {
    'user': {
        'mobile': '00000000011',
        'email': 'email@example.com',
    }
}


def test_company_description_form_cancel_button():
    html = render_to_string('company-profile-description-form.html', {})
    assert 'Cancel' in html


def test_company_logo_form_cancel_button():
    html = render_to_string('company-profile-logo-form.html', {})
    assert 'Cancel' in html


def test_company_profile_details_renders_sectors():
    html = render_to_string('company-profile-details.html', company_context)
    assert 'sector 1' in html
    assert 'sector 2' in html


def test_company_profile_details_handles_no_sectors():
    html = render_to_string('company-profile-details.html', {})
    assert "Edit your company's sectors." in html


def test_company_profile_details_renders_company_number():
    html = render_to_string('company-profile-details.html', company_context)
    assert '123456' in html


def test_company_profile_details_renders_company_name():
    html = render_to_string('company-profile-details.html', company_context)
    assert 'UK exporting co ltd.' in html


def test_company_profile_details_renders_description():
    html = render_to_string('company-profile-details.html', company_context)
    assert 'Exporters of UK wares.' in html


def test_company_profile_details_renders_keywords():
    html = render_to_string('company-profile-details.html', company_context)
    assert "word1 word2" in html


def test_company_profile_details_handles_no_keywords():
    html = render_to_string('company-profile-details.html', {})
    assert "Edit your company's keywords." in html


def test_company_profile_details_renders_website():
    html = render_to_string('company-profile-details.html', company_context)
    assert 'www.ukexportersnow.co.uk' in html


def test_company_profile_details_handles_no_website():
    html = render_to_string('company-profile-details.html', {})
    assert "Edit your company's website address" in html


def test_company_profile_details_renders_logo():
    html = render_to_string('company-profile-details.html', company_context)
    assert 'www.ukexportersnow.co.uk/logo.png' in html


def test_company_profile_details_renders_change_logo_button():
    html = render_to_string('company-profile-details.html', company_context)
    assert 'Change logo' in html


def test_company_profile_details_renders_set_logo_button():
    html = render_to_string('company-profile-details.html', {})
    assert 'Set logo' in html


def test_form_wrapper_next_button():
    context = {
        'wizard': {
            'steps':
                {
                    'step1': 2,
                    'count': 3,
                }
        }
    }
    html = render_to_string('form-wrapper.html', context)
    assert 'value="Next"' in html
    assert 'value="Register"' not in html


def test_form_wrapper_finish_button():
    context = {
        'wizard': {
            'steps':
                {
                    'step1': 3,
                    'count': 3,
                }
        }
    }
    html = render_to_string('form-wrapper.html', context)
    assert 'value="Next"' not in html
    assert 'value="Register"' in html


def test_form_wizard_step_indicator_accessibility_helper():
    context = {
        'wizard': {
            'steps':
                {
                    'step1': 1,
                    'count': 3,
                }
        }
    }
    html = render_to_string('form_wizard_step_indicator.html', context)
    assert 'You are now on step 1 of 3' in html


def test_company_profile_form_supports_file_upload():
    # http://stackoverflow.com/a/5567063/904887
    html = render_to_string('company-profile-form.html', {})
    assert 'enctype="multipart/form-data"' in html


def test_user_form_renders_title():
    html = render_to_string('user-form.html', {})
    assert 'Your details' in html


def test_aims_form_renders_title():
    html = render_to_string('aims-form.html', {})
    assert 'Your exporting aims' in html


def test_company_form_renders_title():
    html = render_to_string('company-form.html', {})
    assert "Create your company’s profile" in html


def test_export_status_form_error():
    form = forms.CompanyExportStatusForm(data={
        'export_status': choices.NO_EXPORT_INTENTION
    })
    context = {
        'form': form
    }
    html = render_to_string('export-status-form.html', context)
    assert 'Try our other business services' in html


def test_export_status_no_form_error_size():
    form = forms.CompanyExportStatusForm(data={
        'export_status': choices.EXPORT_STATUSES[1][0]
    })
    context = {
        'form': form
    }
    html = render_to_string('export-status-form.html', context)
    assert 'Sorry, this is not the right service for your company' not in html
    assert '<form' in html


def test_export_status_common_invalid_form_error_size():
    form = forms.CompanyExportStatusForm(data={
        'export_status': ''
    })
    context = {
        'form': form
    }
    html = render_to_string('export-status-form.html', context)
    assert 'span8' in html
    assert 'Sorry, this is not the right service for your company' not in html
    assert '<form' in html


def test_company_profile_form_correct_title():
    html = render_to_string('company-profile-form.html', {})
    assert 'Your company details' in html


def test_header_logged_in():
    context = {
        'sso_is_logged_in': True,
        'sso_login_url': 'login.com',
        'sso_logout_url': 'logout.com',
    }
    html = render_to_string('header.html', context)
    assert 'Login' not in html
    assert context['sso_login_url'] not in html
    assert 'Logout' in html
    assert context['sso_logout_url'] in html


def test_header_logged_out():
    context = {
        'sso_is_logged_in': False,
        'sso_login_url': 'login.com',
        'sso_logout_url': 'logout.com',
    }
    html = render_to_string('header.html', context)
    assert 'Login' in html
    assert context['sso_login_url'] in html
    assert 'Logout' not in html
    assert context['sso_logout_url'] not in html


def test_google_tag_manager():
    expected_head = render_to_string('google_tag_manager_head.html')
    expected_body = render_to_string('google_tag_manager_body.html')

    html = render_to_string('govuk_layout.html')

    assert expected_head in html
    assert expected_body in html
    # sanity check
    assert 'www.googletagmanager.com' in expected_head
    assert 'www.googletagmanager.com' in expected_body


def test_international_landing_page_renders():
    # confirm the template renders without error
    render_to_string('landing-page-international.html')
