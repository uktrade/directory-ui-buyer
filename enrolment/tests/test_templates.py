import os

from directory_validators.constants import choices

from django.conf import settings
from django.forms import CharField, Form, HiddenInput
from django.template.loader import render_to_string

from enrolment import forms

supplier_context = {
    'supplier': {
        'mobile': '00000000011',
        'email': 'email@example.com',
    }
}


def test_landing_page_includes_hero_links():
    context = {
        'supplier_profile_urls': {
            'immersive': 'http://07723438.com',
            'blippar': 'http://07446749.com',
            'briggs': 'http://06836628.com',
        }
    }
    html = render_to_string('landing-page.html', context)

    for url in context['supplier_profile_urls'].values():
        assert 'href="{0}"'.format(url) in html


def test_company_description_form_cancel_button():
    html = render_to_string('company-profile-description-form.html', {})
    assert 'Cancel' in html


def test_company_logo_form_cancel_button():
    html = render_to_string('company-profile-logo-form.html', {})
    assert 'Cancel' in html


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


def test_company_profile_form_supports_file_upload():
    # http://stackoverflow.com/a/5567063/904887
    html = render_to_string('company-profile-form.html', {})
    assert 'enctype="multipart/form-data"' in html


def test_aims_form_renders_title():
    html = render_to_string('aims-form.html', {})
    assert 'Your exporting aims' in html


def test_company_form_renders_title():
    html = render_to_string('company-form.html', {})
    assert "Create your company’s profile" in html


def test_form_wrapper_hides_hidden_fields():

    class FormWithHiddenField(Form):
        visible = CharField()
        hidden = CharField(widget=HiddenInput())

    context = {
        'form': FormWithHiddenField()
    }
    html = render_to_string('form-wrapper.html', context)

    assert '<label for="id_visible">Visible:</label>' in html
    assert '<label for="id_hidden">Hidden:</label>' not in html


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
    assert 'Sign in' not in html
    assert context['sso_login_url'] not in html
    assert 'Sign out' in html
    assert context['sso_logout_url'] in html


def test_header_logged_out():
    context = {
        'sso_is_logged_in': False,
        'sso_login_url': 'login.com',
        'sso_logout_url': 'logout.com',
    }
    html = render_to_string('header.html', context)
    assert 'Sign in' in html
    assert context['sso_login_url'] in html
    assert 'Sign out' not in html
    assert context['sso_logout_url'] not in html


def test_google_tag_manager_project_id():
    context = {
        'analytics': {
            'GOOGLE_TAG_MANAGER_ID': '123456',
        }
    }
    head_html = render_to_string('google_tag_manager_head.html', context)
    body_html = render_to_string('google_tag_manager_body.html', context)

    assert '123456' in head_html
    assert 'https://www.googletagmanager.com/ns.html?id=123456' in body_html


def test_google_tag_manager():
    expected_head = render_to_string('google_tag_manager_head.html', {})
    expected_body = render_to_string('google_tag_manager_body.html', {})

    html = render_to_string('govuk_layout.html', {})

    assert expected_head in html
    assert expected_body in html
    # sanity check
    assert 'www.googletagmanager.com' in expected_head
    assert 'www.googletagmanager.com' in expected_body


def test_utm_cookie_domain():
    context = {
        'analytics': {
            'UTM_COOKIE_DOMAIN': '.thing.com',
        }
    }
    html = render_to_string('govuk_layout.html', context)

    assert '<meta id="utmCookieDomain" value=".thing.com" />' in html


def test_shared_style_enabled():
    context = {
        'features': {
            'FEATURE_NEW_HEADER_FOOTER_ENABLED': True,
        }
    }

    html = render_to_string('govuk_layout.html', context)

    assert render_to_string('header.html') in html
    assert render_to_string('footer.html') in html
    assert render_to_string('header_old.html') not in html
    assert render_to_string('footer_old.html') not in html


def test_shared_style_disabled():
    context = {
        'features': {
            'FEATURE_NEW_HEADER_FOOTER_ENABLED': False,
        }
    }

    html = render_to_string('govuk_layout.html', context)

    assert render_to_string('header.html') not in html
    assert render_to_string('footer.html') not in html
    assert render_to_string('header_old.html') in html
    assert render_to_string('footer_old.html') in html


def test_enrolment_instructions_page_renders():
    # confirm the template renders without error
    render_to_string('enrolment-instructions.html')


def test_templates_render_successfully():

    template_list = []
    template_dirs = [
        os.path.join(settings.BASE_DIR, 'enrolment/templates'),
        os.path.join(settings.BASE_DIR, 'supplier/templates'),
    ]
    for template_dir in template_dirs:
        for dir, dirnames, filenames in os.walk(template_dir):
            for filename in filenames:
                path = os.path.join(dir, filename).replace(template_dir, '')
                template_list.append(path.lstrip('/'))

    default_context = {
        'supplier': None,
        'form': Form(),
    }
    assert template_list
    for template in template_list:
        render_to_string(template, default_context)


def test_form_progress_indicator_no_steps():
    context = {}
    html = render_to_string('form_progress_indicator.html', context)
    assert html.strip() == ''


def test_form_progress_indicator_first_step_active():
    context = {
        'form_labels': ['one', 'two', 'three'],
        'wizard': {
            'steps':
                {
                    'step1': 1,
                    'count': 3,
                }
        }
    }
    html = render_to_string('form_progress_indicator.html', context)

    assert html.count('ed-form-progress-indicator-line') == 1
    assert html.count('ed-form-progress-indicator-active') == 1
    assert html.count('ed-form-progress-indicator-prev') == 0


def test_form_progress_indicator_second_step_active():
    context = {
        'form_labels': ['one', 'two', 'three'],
        'wizard': {
            'steps':
                {
                    'step1': 2,
                    'count': 3,
                }
        }
    }
    html = render_to_string('form_progress_indicator.html', context)

    assert html.count('ed-form-progress-indicator-line') == 2
    assert html.count('ed-form-progress-indicator-active') == 1
    assert html.count('ed-form-progress-indicator-prev') == 1


def test_form_progress_indicator_last_step_active():
    context = {
        'form_labels': ['one', 'two', 'three'],
        'wizard': {
            'steps':
                {
                    'step1': 3,
                    'count': 3,
                }
        }
    }
    html = render_to_string('form_progress_indicator.html', context)

    assert html.count('ed-form-progress-indicator-line') == 3
    assert html.count('ed-form-progress-indicator-active') == 1
    assert html.count('ed-form-progress-indicator-prev') == 2
