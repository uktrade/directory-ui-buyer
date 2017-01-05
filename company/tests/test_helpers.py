from datetime import datetime

import requests
import pytest

from company import helpers


@pytest.fixture
def profile_data():
    return {
        'website': 'http://www.example.com',
        'description': 'bloody good',
        'summary': 'good',
        'number': '01234567',
        'date_of_creation': '2010-10-10',
        'sectors': ['AGRICULTURE_HORTICULTURE_AND_FISHERIES'],
        'logo': 'nice.png',
        'name': 'Great corp',
        'keywords': 'I found it most pleasing, hi',
        'employees': '1001-10000',
        'supplier_case_studies': [],
        'modified': '2016-11-23T11:21:10.977518Z',
        'verified_with_code': True,
        'twitter_url': 'http://www.twitter.com',
        'facebook_url': 'http://www.facebook.com',
        'linkedin_url': 'http://www.linkedin.com',
        'contact_details': {
            'email_address': 'sales@example.com',
        },
    }


@pytest.fixture
def public_companies(profile_data):
    return {
        'count': 100,
        'results': [profile_data]
    }


@pytest.fixture
def public_companies_empty():
    return {
        'count': 0,
        'results': []
    }


def test_get_employees_label():
    assert helpers.get_employees_label('1001-10000') == '1,001-10,000'


def test_pair_sector_values_with_label():
    values = ['AGRICULTURE_HORTICULTURE_AND_FISHERIES', 'AEROSPACE']
    expected = [
        {
            'label': 'Agriculture, horticulture and fisheries',
            'value': 'AGRICULTURE_HORTICULTURE_AND_FISHERIES',
        },
        {
            'label': 'Aerospace',
            'value': 'AEROSPACE',
        }
    ]
    assert helpers.pair_sector_values_with_label(values) == expected


def test_get_employees_label_none():
    assert helpers.get_employees_label('') == ''


def test_pair_sector_values_with_label_empty():
    for value in [None, []]:
        assert helpers.pair_sector_values_with_label(value) == []


def test_get_company_profile_from_response(profile_data):
    response = requests.Response()
    response.json = lambda: profile_data
    expected = {
        'website': 'http://www.example.com',
        'description': 'bloody good',
        'summary': 'good',
        'number': '01234567',
        'date_of_creation': datetime(2010, 10, 10),
        'sectors': [
            {
                'label': 'Agriculture, horticulture and fisheries',
                'value': 'AGRICULTURE_HORTICULTURE_AND_FISHERIES',
            }
        ],
        'logo': 'nice.png',
        'name': 'Great corp',
        'keywords': 'I found it most pleasing, hi',
        'employees': '1,001-10,000',
        'supplier_case_studies': [],
        'modified': datetime(2016, 11, 23, 11, 21, 10, 977518),
        'verified_with_code': True,
        'is_address_set': True,
        'contact_details': {
            'email_address': 'sales@example.com',
        },
        'twitter_url': 'http://www.twitter.com',
        'facebook_url': 'http://www.facebook.com',
        'linkedin_url': 'http://www.linkedin.com',
    }
    actual = helpers.get_company_profile_from_response(response)
    assert actual == expected


def test_get_public_company_profile_from_response(profile_data):
    response = requests.Response()
    response.json = lambda: profile_data
    expected = {
        'website': 'http://www.example.com',
        'description': 'bloody good',
        'summary': 'good',
        'number': '01234567',
        'date_of_creation': datetime(2010, 10, 10),
        'sectors': [
            {
                'label': 'Agriculture, horticulture and fisheries',
                'value': 'AGRICULTURE_HORTICULTURE_AND_FISHERIES',
            }
        ],
        'logo': 'nice.png',
        'name': 'Great corp',
        'keywords': 'I found it most pleasing, hi',
        'employees': '1,001-10,000',
        'supplier_case_studies': [],
        'modified': datetime(2016, 11, 23, 11, 21, 10, 977518),
        'verified_with_code': True,
        'is_address_set': True,
        'contact_details': {
            'email_address': 'sales@example.com',
        },
        'twitter_url': 'http://www.twitter.com',
        'facebook_url': 'http://www.facebook.com',
        'linkedin_url': 'http://www.linkedin.com',
    }
    actual = helpers.get_public_company_profile_from_response(response)
    assert actual == expected


def test_get_company_list_from_response(public_companies):
    response = requests.Response()
    response.json = lambda: public_companies
    expected = {
        'count': 100,
        'results': [
            {
                'website': 'http://www.example.com',
                'description': 'bloody good',
                'summary': 'good',
                'number': '01234567',
                'date_of_creation': datetime(2010, 10, 10),
                'sectors': [
                    {
                        'label': 'Agriculture, horticulture and fisheries',
                        'value': 'AGRICULTURE_HORTICULTURE_AND_FISHERIES',
                    }
                ],
                'logo': 'nice.png',
                'name': 'Great corp',
                'keywords': 'I found it most pleasing, hi',
                'employees': '1,001-10,000',
                'supplier_case_studies': [],
                'modified': datetime(2016, 11, 23, 11, 21, 10, 977518),
                'verified_with_code': True,
                'is_address_set': True,
                'contact_details': {
                    'email_address': 'sales@example.com'
                },
                'twitter_url': 'http://www.twitter.com',
                'facebook_url': 'http://www.facebook.com',
                'linkedin_url': 'http://www.linkedin.com',
            }
        ]
    }
    actual = helpers.get_company_list_from_response(response)
    assert actual == expected


def test_get_company_list_from_response_empty(public_companies_empty):
    response = requests.Response()
    response.json = lambda: public_companies_empty
    expected = {
        'count': 0,
        'results': [],
    }
    actual = helpers.get_company_list_from_response(response)
    assert actual == expected


def test_get_company_profile_from_response_without_date(profile_data):
    pairs = [
        ['2010-10-10', datetime(2010, 10, 10)],
        ['', ''],
        [None, None],
    ]
    for provided, expected in pairs:
        assert helpers.format_date_of_creation(provided) == expected


def test_format_company_details_address_set(profile_data):
    profile_data['contact_details'] = {'key': 'value'}
    actual = helpers.format_company_details(profile_data)

    assert actual['is_address_set'] is True


def test_format_company_details_address_not_set(profile_data):
    profile_data['contact_details'] = {}
    actual = helpers.format_company_details(profile_data)

    assert actual['is_address_set'] is False


def test_format_company_details_none_address_not_set(profile_data):
    profile_data['contact_details'] = None
    actual = helpers.format_company_details(profile_data)

    assert actual['is_address_set'] is False


def test_format_case_study(supplier_case_study_data, settings):
    settings.SUPPLIER_CASE_STUDY_URL = 'http://case_study.com/{id}'
    settings.SUPPLIER_PROFILE_LIST_URL = 'http://list.com/{sectors}'
    actual = helpers.format_case_study(supplier_case_study_data)
    assert actual['sector'] == {
        'label': 'Software and computer services',
        'url': 'http://list.com/SOFTWARE_AND_COMPUTER_SERVICES',
    }
    assert actual['url'] == 'http://case_study.com/2'
