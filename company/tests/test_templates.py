from datetime import datetime, timedelta

from django.core.urlresolvers import reverse
from django.template.loader import render_to_string


default_context = {
    'company': {
        'sectors': [
            {'value': 'SECTOR1', 'label': 'sector 1'},
            {'value': 'SECTOR2', 'label': 'sector 2'},
        ],
        'employees': '1-10',
        'number': '123456',
        'name': 'UK exporting co ltd.',
        'summary': 'Exporters of UK wares.',
        'website': 'www.ukexportersnow.co.uk',
        'logo': 'www.ukexportersnow.co.uk/logo.png',
        'keywords': 'word1 word2',
        'date_of_creation': datetime(2015, 3, 2),
        'modified': datetime.now() - timedelta(hours=1),
        'contact_details': {
            'email_address': 'sales@example.com',
        },
        'is_published': False,
        'twitter_url': 'https://www.twitter.com',
        'facebook_url': 'https://www.facebook.com',
        'linkedin_url': 'https://www.linkedin.com',
        'public_profile_url': 'http://www.example.com/profile'
    }
}

DATE_CREATED_LABEL = 'Incorporated'
NO_RESULTS_FOUND_LABEL = 'No companies found'
CONTACT_LINK_LABEL = 'Contact company'
UPDATED_LABEL = 'Last updated'


def test_company_profile_details_renders_public_link_if_published():
    template_name = 'company-private-profile-detail.html'
    context = {
        'company': {
            'summary': 'thing',
            'public_profile_url': 'http://www.example.com/profile',
            'is_published': True,
        }
    }
    html = render_to_string(template_name, context)

    assert html.count('href="http://www.example.com/profile"') == 2


def test_company_profile_details_not_render_public_link_if_published():
    template_name = 'company-private-profile-detail.html'
    context = {
        'company': {
            'public_profile_url': 'http://www.example.com/profile',
            'is_published': False,
        }
    }
    html = render_to_string(template_name, context)

    assert html.count('href="http://www.example.com/profile"') == 0


def test_company_profile_details_renders_social_links():
    edit_url = reverse('company-edit-social-media')
    template_name = 'company-private-profile-detail.html'
    context = default_context

    html = render_to_string(template_name, context)

    assert context['company']['twitter_url'] in html
    assert context['company']['facebook_url'] in html
    assert context['company']['linkedin_url'] in html
    assert html.count(edit_url) == 1


def test_company_profile_details_renders_edit_social_links():
    edit_url = reverse('company-edit-social-media')
    template_name = 'company-private-profile-detail.html'
    context = {}

    html = render_to_string(template_name, context)

    assert html.count(edit_url) == 4


def test_company_profile_details_renders_contact_details():
    template_name = 'company-private-profile-detail.html'
    context = default_context

    html = render_to_string(template_name, context)

    assert context['company']['website'] in html
    assert context['company']['contact_details']['email_address'] in html


def test_company_profile_details_renders_company_details():
    template_name = 'company-private-profile-detail.html'
    context = default_context

    html = render_to_string(template_name, context)

    assert context['company']['employees'] in html
    assert context['company']['number'] in html


def test_company_profile_details_renders_company_name():
    template_name = 'company-private-profile-detail.html'
    html = render_to_string(template_name, default_context)
    assert default_context['company']['name'] in html


def test_company_profile_details_renders_logo():
    template_name = 'company-private-profile-detail.html'
    html = render_to_string(template_name, default_context)

    assert default_context['company']['logo'] in html


def test_company_profile_details_renders_summary():
    template_name = 'company-private-profile-detail.html'
    html = render_to_string(template_name, default_context)
    assert default_context['company']['summary'] in html


def test_company_profile_details_renders_sectors():
    template_name = 'company-private-profile-detail.html'
    html = render_to_string(template_name, default_context)
    assert 'sector 1' in html
    assert 'sector 2' in html


def test_company_profile_details_renders_keywords():
    template_name = 'company-private-profile-detail.html'
    html = render_to_string(template_name, default_context)
    assert default_context['company']['keywords'] in html


def test_company_private_profile_details_renders_standalone_edit_links():
    context = {'show_wizard_links': False}
    html = render_to_string('company-private-profile-detail.html', context)

    assert reverse('company-edit-address') in html
    assert reverse('company-edit-sectors') in html
    assert reverse('company-edit-key-facts') in html


def test_company_private_profile_details_renders_wizard_links():
    context = {'show_wizard_links': True}
    html = render_to_string('company-private-profile-detail.html', context)
    company_edit_link = 'href="{url}"'.format(url=reverse('company-edit'))

    assert reverse('company-edit-address') not in html
    assert reverse('company-edit-sectors') not in html
    assert reverse('company-edit-key-facts') not in html
    assert html.count(company_edit_link) == 9
