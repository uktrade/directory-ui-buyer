from datetime import datetime, timedelta

import pytest

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
        'keywords': 'word1, word2',
        'date_of_creation': datetime(2015, 3, 2),
        'modified': datetime.now() - timedelta(hours=1),
        'email_address': 'sales@example.com',
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
    template_name = 'company-profile-detail.html'
    context = {
        'company': {
            'summary': 'thing',
            'public_profile_url': 'http://www.example.com/profile',
            'is_published': True,
        }
    }
    html = render_to_string(template_name, context)

    assert html.count('href="http://www.example.com/profile"') == 3


def test_company_profile_details_not_render_public_link_if_published():
    template_name = 'company-profile-detail.html'
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
    template_name = 'company-profile-detail.html'
    context = default_context

    html = render_to_string(template_name, context)

    assert context['company']['twitter_url'] in html
    assert context['company']['facebook_url'] in html
    assert context['company']['linkedin_url'] in html
    assert html.count(edit_url) == 1


def test_company_profile_details_renders_edit_social_links():
    edit_url = reverse('company-edit-social-media')
    template_name = 'company-profile-detail.html'
    context = {}

    html = render_to_string(template_name, context)

    assert html.count(edit_url) == 4


def test_company_profile_details_renders_contact_details():
    template_name = 'company-profile-detail.html'
    context = default_context

    html = render_to_string(template_name, context)

    assert context['company']['website'] in html
    assert context['company']['email_address'] in html


def test_company_profile_details_renders_company_details():
    template_name = 'company-profile-detail.html'
    context = default_context

    html = render_to_string(template_name, context)

    assert context['company']['employees'] in html
    assert context['company']['number'] in html


def test_company_profile_details_renders_company_name():
    template_name = 'company-profile-detail.html'
    html = render_to_string(template_name, default_context)
    assert default_context['company']['name'] in html


def test_company_profile_details_renders_logo():
    template_name = 'company-profile-detail.html'
    html = render_to_string(template_name, default_context)

    assert default_context['company']['logo'] in html


def test_company_profile_details_renders_summary():
    template_name = 'company-profile-detail.html'
    html = render_to_string(template_name, default_context)
    assert default_context['company']['summary'] in html


def test_company_profile_details_renders_sectors():
    template_name = 'company-profile-detail.html'
    html = render_to_string(template_name, default_context)
    assert 'sector 1' in html
    assert 'sector 2' in html


def test_company_profile_details_renders_keywords():
    template_name = 'company-profile-detail.html'
    html = render_to_string(template_name, default_context)

    assert default_context['company']['keywords']
    for keyword in default_context['company']['keywords']:
        assert keyword in html


def test_company_private_profile_details_renders_standalone_edit_links():
    context = {
        'show_wizard_links': False,
        'company': {
            'description': 'description description',
            'summary': 'summary summary',
            'email_address': 'thing@example.com',
            'verified_with_code': False,
            'is_published': False,
        }
    }
    html = render_to_string('company-profile-detail.html', context)

    assert reverse('company-edit-address') in html
    assert reverse('company-edit-sectors') in html
    assert reverse('company-edit-key-facts') in html


def test_company_private_profile_details_renders_wizard_links():
    context = {
        'show_wizard_links': True,
        'company': {
            'description': 'description description',
            'summary': 'summary summary',
            'email_address': 'thing@example.com',
            'verified_with_code': False,
            'is_published': False,
        }
    }
    html = render_to_string('company-profile-detail.html', context)
    company_edit_link = 'href="{url}"'.format(url=reverse('company-edit'))

    assert reverse('company-edit-sectors') not in html
    assert reverse('company-edit-key-facts') not in html
    assert html.count(company_edit_link) == 7


def test_company_profile_unpublished_no_description():
    context = {
        'company': {
            'is_published': False,
            'description': '',
            'summary': '',
        }
    }
    template_name = 'company-profile-detail.html'

    html = render_to_string(template_name, context)

    assert 'Your company has no description' in html


def test_company_profile_unpublished_no_email():
    context = {
        'company': {
            'is_published': False,
            'description': 'description description',
            'summary': 'summary summary',
            'email_address': ''
        }
    }
    template_name = 'company-profile-detail.html'

    html = render_to_string(template_name, context)

    assert 'Your company has no contact details' in html


@pytest.mark.parametrize("is_verified,should_show_message", [
    [True, False],
    [False, True],
])
def test_company_profile_unpublished_not_verified(
    is_verified, should_show_message
):
    context = {
        'company': {
            'is_published': False,
            'description': 'description description',
            'summary': 'summary summary',
            'email_address': 'thing@example.com',
            'is_verified': is_verified,
        }
    }
    template_name = 'company-profile-detail.html'

    html = render_to_string(template_name, context)

    label = 'Your company has not yet been verified'
    assert (label in html) is should_show_message


def test_company_profile_unpublished_published():
    context = {
        'company': {
            'is_published': True,
        }
    }
    template_name = 'company-profile-detail.html'

    html = render_to_string(template_name, context)

    assert 'Your company is published' in html


def test_company_profile_details_feature_flag_on():
    template_name = 'company-profile-detail.html'
    context = {
        'features': {
            'FEATURE_COMPANIES_HOUSE_OAUTH2_ENABLED': True,
        },
        'company': {
            'description': 'thing',
            'summary': 'thing',
            'email_address': 'thing@example.com',
        },
    }

    html = render_to_string(template_name, context)

    assert '"' + reverse('verify-company-hub') + '"' in html


def test_company_profile_details_feature_flag_off_valid_address():
    template_name = 'company-profile-detail.html'
    context = {
        'features': {
            'FEATURE_COMPANIES_HOUSE_OAUTH2_ENABLED': False,
        },
        'company': {
            'description': 'thing',
            'summary': 'thing',
            'email_address': 'thing@example.com',
            'has_valid_address': True
        },
    }

    html = render_to_string(template_name, context)

    assert '"' + reverse('verify-company-hub') + '"' not in html
    assert reverse('verify-company-address-confirm') in html
    assert reverse('company-edit-address') not in html


def test_company_profile_details_feature_flag_off_invalid_address():
    template_name = 'company-profile-detail.html'
    context = {
        'features': {
            'FEATURE_COMPANIES_HOUSE_OAUTH2_ENABLED': False,
        },
        'company': {
            'description': 'thing',
            'summary': 'thing',
            'email_address': 'thing@example.com',
            'has_valid_address': False
        },
    }

    html = render_to_string(template_name, context)

    assert '"' + reverse('verify-company-hub') + '"' not in html
    assert reverse('verify-company-address-confirm') not in html
    assert reverse('company-edit-address') in html


def test_company_verify_hub_letter_sent():
    template_name = 'company-verify-hub.html'
    context = {
        'company': {
            'is_verification_letter_sent': True,
        }
    }

    html = render_to_string(template_name, context)

    assert reverse('verify-company-address-confirm') in html
    assert reverse('verify-companies-house') in html


def test_company_verify_hub_letter_not_sent():
    template_name = 'company-verify-hub.html'
    context = {
        'company': {
            'is_verification_letter_sent': False,
        }
    }

    html = render_to_string(template_name, context)

    assert reverse('verify-company-address') in html
    assert reverse('verify-companies-house') in html
