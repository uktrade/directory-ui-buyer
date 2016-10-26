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
    }
}

user_context = {
    'user': {
        'mobile': '00000000011',
        'email': 'email@example.com',
    }
}


def test_company_profile_details_renders_sector():
    html = render_to_string('company-profile-details.html', company_context)
    assert 'sector 1' in html
    assert 'sector 2' in html


def test_company_profile_details_renders_company_number():
    html = render_to_string('company-profile-details.html', company_context)
    assert '123456' in html


def test_company_profile_details_renders_company_name():
    html = render_to_string('company-profile-details.html', company_context)
    assert 'UK exporting co ltd.' in html


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


def test_company_profile_details_handles_no_website():
    html = render_to_string('company-profile-details.html', {})
    assert 'Please set your website address.' in html


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
    assert 'About you' in html


def test_aims_form_renders_title():
    html = render_to_string('aims-form.html', {})
    assert 'Your exporting aims' in html


def test_company_form_renders_title():
    html = render_to_string('company-form.html', {})
    assert 'Join the UK Exporter Directory' in html


def test_export_status_form_error_size():
    form = forms.CompanyExportStatusForm(data={
        'export_status': choices.NO_EXPORT_INTENTION
    })
    context = {
        'form': form
    }
    html = render_to_string('export-status-form.html', context)
    assert 'span12' in html
    assert 'Sorry, this is not the right service for your company' in html


def test_export_status_no_form_error_size():
    form = forms.CompanyExportStatusForm(data={
        'export_status': choices.EXPORT_STATUSES[1][0]
    })
    context = {
        'form': form
    }
    html = render_to_string('export-status-form.html', context)
    assert 'span8' in html
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
