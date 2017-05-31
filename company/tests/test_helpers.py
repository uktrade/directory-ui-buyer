from datetime import datetime

import requests
import pytest

from company import helpers


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


def test_get_company_profile_from_response(
    api_response_company_profile_200, settings
):
    settings.SUPPLIER_PROFILE_URL = 'http://profile.com/{number}'
    response = api_response_company_profile_200
    expected = {
        'public_profile_url': 'http://profile.com/123456',
        'linkedin_url': 'http://www.linkedin.com',
        'has_valid_address': True,
        'country': 'GB',
        'email_full_name': 'Jeremy',
        'locality': 'London',
        'name': 'Great company',
        'modified': datetime(2016, 11, 23, 11, 21, 10, 977518),
        'website': 'http://example.com',
        'postal_code': 'E14 6XK',
        'mobile_number': '07507694377',
        'supplier_case_studies': [],
        'verified_with_code': True,
        'sectors': [{'value': 'SECURITY', 'label': 'Security'}],
        'number': 123456,
        'postal_full_name': 'Jeremy',
        'po_box': '',
        'keywords': ['word1', 'word2'],
        'is_published': True,
        'employees': '501-1,000',
        'twitter_url': 'http://www.twitter.com',
        'date_of_creation': datetime(2015, 3, 2, 0, 0),
        'email_address': 'test@example.com',
        'address_line_2': 'Fakeville',
        'address_line_1': '123 Fake Street',
        'summary': 'good',
        'logo': 'nice.jpg',
        'facebook_url': 'http://www.facebook.com',
        'description': 'Ecommerce website',
    }
    actual = helpers.get_company_profile_from_response(response)

    assert actual == expected


def test_get_public_company_profile_from_response(
    api_response_company_profile_200, settings
):
    settings.SUPPLIER_PROFILE_URL = 'http://profile.com/{number}'
    response = api_response_company_profile_200
    expected = {
        'sectors': [{'value': 'SECURITY', 'label': 'Security'}],
        'email_full_name': 'Jeremy',
        'website': 'http://example.com',
        'date_of_creation': datetime(2015, 3, 2),
        'supplier_case_studies': [],
        'public_profile_url': 'http://profile.com/123456',
        'linkedin_url': 'http://www.linkedin.com',
        'logo': 'nice.jpg',
        'summary': 'good',
        'keywords': ['word1', 'word2'],
        'twitter_url': 'http://www.twitter.com',
        'mobile_number': '07507694377',
        'postal_code': 'E14 6XK',
        'address_line_1': '123 Fake Street',
        'address_line_2': 'Fakeville',
        'country': 'GB',
        'postal_full_name': 'Jeremy',
        'description': 'Ecommerce website',
        'po_box': '',
        'has_valid_address': True,
        'modified': datetime(2016, 11, 23, 11, 21, 10, 977518),
        'locality': 'London',
        'is_published': True,
        'number': 123456,
        'verified_with_code': True,
        'email_address': 'test@example.com',
        'employees': '501-1,000',
        'name': 'Great company',
        'facebook_url': 'http://www.facebook.com',
    }
    actual = helpers.get_public_company_profile_from_response(response)
    assert actual == expected


def test_get_company_list_from_response(api_response_list_public_profile_200,
                                        settings):
    settings.SUPPLIER_PROFILE_URL = 'http://profile.com/{number}'
    response = api_response_list_public_profile_200
    expected = {
        'results': [
            {
                'sectors': [{'value': 'SECURITY', 'label': 'Security'}],
                'email_full_name': 'Jeremy',
                'website': 'http://example.com',
                'date_of_creation': datetime(2015, 3, 2),
                'supplier_case_studies': [],
                'public_profile_url': 'http://profile.com/123456',
                'linkedin_url': 'http://www.linkedin.com',
                'logo': 'nice.jpg',
                'summary': 'good',
                'keywords': ['word1', 'word2'],
                'twitter_url': 'http://www.twitter.com',
                'mobile_number': '07507694377',
                'postal_code': 'E14 6XK',
                'address_line_1': '123 Fake Street',
                'address_line_2': 'Fakeville',
                'country': 'GB',
                'postal_full_name': 'Jeremy',
                'description': 'Ecommerce website',
                'po_box': '',
                'has_valid_address': True,
                'modified': datetime(2016, 11, 23, 11, 21, 10, 977518),
                'locality': 'London',
                'is_published': True,
                'number': 123456,
                'verified_with_code': True,
                'email_address': 'test@example.com',
                'employees': '501-1,000',
                'name': 'Great company',
                'facebook_url': 'http://www.facebook.com',
            }
        ],
        'count': 20
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


def test_get_company_profile_from_response_without_date():
    pairs = [
        ['2010-10-10', datetime(2010, 10, 10)],
        ['', ''],
        [None, None],
    ]
    for provided, expected in pairs:
        assert helpers.format_date_of_creation(provided) == expected


def test_format_case_study(supplier_case_study_data, settings):
    settings.SUPPLIER_CASE_STUDY_URL = 'http://case_study.com/{id}'
    settings.SUPPLIER_PROFILE_LIST_URL = 'http://list.com/{sectors}'
    actual = helpers.format_case_study(supplier_case_study_data)
    assert actual['sector'] == {
        'label': 'Software and computer services',
        'url': 'http://list.com/SOFTWARE_AND_COMPUTER_SERVICES',
    }
    assert actual['url'] == 'http://case_study.com/2'


def test_chunk_list():
    input_list = [1, 2, 3, 4, 5, 6, 7, 8]
    expected_list = [[1, 2, 3], [4, 5, 6], [7, 8]]
    assert helpers.chunk_list(input_list, 3) == expected_list


def test_chunk_list_empty():
    input_list = []
    expected_list = []
    assert helpers.chunk_list(input_list, 3) == expected_list


def test_format_company_details_handles_keywords_empty(retrieve_profile_data):
    for value in ['', None, []]:
        retrieve_profile_data['keywords'] = value

        formatted = helpers.format_company_details(retrieve_profile_data)

        assert formatted['keywords'] == []
