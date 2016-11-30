from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from django.template.loader import render_to_string

from company import forms


default_context = {
    'company': {
        'sectors': [
            {'value': 'SECTOR1', 'label': 'sector 1'},
            {'value': 'SECTOR2', 'label': 'sector 2'},
        ],
        'number': '123456',
        'name': 'UK exporting co ltd.',
        'description': 'Exporters of UK wares.',
        'website': 'www.ukexportersnow.co.uk',
        'logo': 'www.ukexportersnow.co.uk/logo.png',
        'keywords': 'word1 word2',
        'date_of_creation': '2 Mar 2015',
    }
}

EDIT_KEYWORDS_LABEL = "Edit your company's keywords."
EDIT_SECTORS_LABEL = "Edit your company's sectors."
EDIT_WEBSITE_LABEL = "Edit your company's website address"
DATE_CREATED_LABEL = 'Date incorporated'
CHANGE_LOGO_LABEL = 'Change logo'
SET_LOGO_MESSAGE = 'Set logo'
NO_RESULTS_FOUND_LABEL = 'No companies found'


def test_company_profile_details_feature_flag_public_profile_on():
    context = {
        'company': {
            'sectors': [
                {'value': 'THING', 'label': 'thing'},
                {'value': 'OTHER_THING', 'label': 'other_thing'},
            ]
        },
        'features': {
            'FEATURE_PUBLIC_PROFILES': True
        }
    }
    url = reverse('public-company-profiles-list')
    html = render_to_string('company-profile-detail.html', context)

    assert 'href="{url}?sectors=THING"'.format(url=url) in html
    assert 'href="{url}?sectors=OTHER_THING"'.format(url=url) in html


def test_company_profile_details_feature_flag_public_profile_off():
    context = {
        'company': {
            'sectors': [
                {'value': 'THING', 'label': 'thing'},
                {'value': 'OTHER_THING', 'label': 'other_thing'},
            ]
        },
        'features': {
            'FEATURE_PUBLIC_PROFILES': False
        }
    }
    url = reverse('public-company-profiles-list')
    html = render_to_string('company-profile-detail.html', context)

    assert 'href="{url}?sectors=THING"'.format(url=url) not in html
    assert 'href="{url}?sectors=OTHER_THING"'.format(url=url) not in html


def test_company_profile_details_renders_sectors():
    html = render_to_string('company-profile-detail.html', default_context)
    assert 'sector 1' in html
    assert 'sector 2' in html


def test_company_profile_details_renders_date_created():
    html = render_to_string('company-profile-detail.html', default_context)
    assert '2 Mar 2015' in html
    assert DATE_CREATED_LABEL in html


def test_company_profile_details_handles_no_date_created():
    html = render_to_string('company-profile-detail.html')
    assert DATE_CREATED_LABEL not in html


def test_company_profile_details_handles_no_sectors_show_edit_links():
    context = {'show_edit_links': True}
    html = render_to_string('company-profile-detail.html', context)
    assert EDIT_SECTORS_LABEL in html


def test_company_profile_details_handles_no_sectors_hide_edit_links():
    context = {'show_edit_links': False}
    html = render_to_string('company-profile-detail.html', context)
    assert EDIT_SECTORS_LABEL not in html


def test_company_profile_details_renders_company_number():
    html = render_to_string('company-profile-detail.html', default_context)
    assert default_context['company']['number'] in html


def test_company_profile_details_renders_company_name():
    html = render_to_string('company-profile-detail.html', default_context)
    assert default_context['company']['name'] in html


def test_company_profile_details_renders_description():
    html = render_to_string('company-profile-detail.html', default_context)
    assert default_context['company']['description'] in html


def test_company_profile_details_renders_keywords():
    html = render_to_string('company-profile-detail.html', default_context)
    assert default_context['company']['keywords'] in html


def test_company_profile_details_handles_no_keywords_show_edit_links():
    context = {'show_edit_links': True}
    html = render_to_string('company-profile-detail.html', context)
    assert EDIT_KEYWORDS_LABEL in html


def test_company_profile_details_handles_no_keywords_hide_edit_links():
    context = {'show_edit_links': False}
    html = render_to_string('company-profile-detail.html', context)
    assert EDIT_KEYWORDS_LABEL not in html


def test_company_profile_details_renders_website():
    html = render_to_string('company-profile-detail.html', default_context)
    assert default_context['company']['website'] in html


def test_company_profile_details_handles_no_website_show_edit_links():
    context = {'show_edit_links': True}
    html = render_to_string('company-profile-detail.html', context)
    assert EDIT_WEBSITE_LABEL in html


def test_company_profile_details_handles_no_website_hide_edit_links():
    context = {'show_edit_links': False}
    html = render_to_string('company-profile-detail.html', context)
    assert EDIT_WEBSITE_LABEL not in html


def test_company_profile_details_renders_website_hide_edit_links():
    context = {
        'show_edit_links': False,
        'company': {
            'website': ''
        },
    }
    html = render_to_string('company-profile-detail.html', context)
    assert EDIT_WEBSITE_LABEL not in html


def test_company_profile_details_renders_website_show_edit_links():
    context = {
        'show_edit_links': True,
        'company': {
            'website': ''
        },
    }
    html = render_to_string('company-profile-detail.html', context)
    assert EDIT_WEBSITE_LABEL in html


def test_company_profile_details_renders_logo():
    html = render_to_string('company-profile-detail.html', default_context)
    assert default_context['company']['logo'] in html


def test_company_profile_details_renders_change_logo_button_show_edit_links():
    context = {
        'show_edit_links': True,
        'company': {
            'logo': default_context['company']['logo'],
        }
    }
    html = render_to_string('company-profile-detail.html', context)
    assert CHANGE_LOGO_LABEL in html


def test_company_profile_details_renders_change_logo_button_hide_edit_links():
    context = {
        'show_edit_links': False,
        'company': {
            'logo': default_context['company']['logo'],
        }
    }
    html = render_to_string('company-profile-detail.html', context)
    assert CHANGE_LOGO_LABEL not in html


def test_company_profile_details_renders_set_logo_button_show_edit_links():
    context = {
        'show_edit_links': True,
    }
    html = render_to_string('company-profile-detail.html', context)
    assert SET_LOGO_MESSAGE in html


def test_company_profile_details_renders_set_logo_button_hide_edit_links():
    context = {
        'show_edit_links': False,
    }
    html = render_to_string('company-profile-detail.html', context)
    assert SET_LOGO_MESSAGE not in html


def test_company_public_profile_list_link_to_profle():
    context = {
        'companies': [
            default_context['company']
        ]
    }
    url = reverse(
        'public-company-profiles-detail',
        kwargs={'company_number': default_context['company']['number']}
    )
    html = render_to_string('company-public-profile-list.html', context)

    assert 'href="{url}"'.format(url=url) in html


def test_company_public_profile_no_results_label():
    form = forms.PublicProfileSearchForm(data={'sectors': 'WATER'})
    assert form.is_valid()
    context = {
        'companies': [],
        'form': form,
    }
    html = render_to_string('company-public-profile-list.html', context)

    assert NO_RESULTS_FOUND_LABEL in html


def test_company_public_profile_results_label():
    form = forms.PublicProfileSearchForm(data={'sectors': 'WATER'})
    assert form.is_valid()
    paginator = Paginator([{}], 10)
    context = {
        'selected_sector_label': 'thing',
        'companies':  [
            default_context['company']
        ],
        'pagination': paginator.page(1),
        'form': form,
    }
    html = render_to_string('company-public-profile-list.html', context)
    assert "Displaying 1 of 1 \'thing\' company" in html
    assert NO_RESULTS_FOUND_LABEL not in html


def test_company_public_profile_results_label_plural():
    form = forms.PublicProfileSearchForm(data={'sectors': 'WATER'})
    assert form.is_valid()
    paginator = Paginator(range(10), 10)
    context = {
        'selected_sector_label': 'thing',
        'companies': [
            default_context['company'],
            default_context['company'],
        ],
        'pagination': paginator.page(1),
        'form': form,
    }
    html = render_to_string('company-public-profile-list.html', context)
    assert "Displaying 2 of 10 \'thing\' companies" in html
    assert NO_RESULTS_FOUND_LABEL not in html


def test_company_public_profile_list_paginate_next():
    form = forms.PublicProfileSearchForm(data={'sectors': 'WATER'})
    assert form.is_valid()

    paginator = Paginator(range(100), 10)
    context = {
        'pagination': paginator.page(1),
        'form': form,
        'companies': [{'number': '01234567A'}]
    }

    html = render_to_string('company-public-profile-list.html', context)

    assert 'href="?sectors=WATER&page=2"' in html


def test_company_public_profile_list_paginate_prev():
    form = forms.PublicProfileSearchForm(data={'sectors': 'WATER'})
    assert form.is_valid()

    paginator = Paginator(range(100), 10)
    context = {
        'pagination': paginator.page(2),
        'form': form,
        'companies': [{'number': '01234567A'}]
    }

    html = render_to_string('company-public-profile-list.html', context)

    assert 'href="?sectors=WATER&page=1"' in html
