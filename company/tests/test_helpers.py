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
        'address_line_1': '123 Fake Street',
        'address_line_2': 'Fakeville',
        'country': 'GB',
        'date_of_creation': datetime(2015, 3, 2, 0, 0),
        'description': 'Ecommerce website',
        'email_address': 'test@example.com',
        'email_full_name': 'Jeremy',
        'employees': '501-1,000',
        'facebook_url': 'http://www.facebook.com',
        'has_valid_address': True,
        'is_published': True,
        'is_verification_letter_sent': False,
        'is_verified': True,
        'keywords': ['word1', 'word2'],
        'linkedin_url': 'http://www.linkedin.com',
        'locality': 'London',
        'logo': 'nice.jpg',
        'mobile_number': '07507694377',
        'modified': datetime(2016, 11, 23, 11, 21, 10, 977518),
        'name': 'Great company',
        'number': 123456,
        'po_box': '',
        'postal_code': 'E14 6XK',
        'postal_full_name': 'Jeremy',
        'public_profile_url': 'http://profile.com/123456',
        'sectors': [{'value': 'SECURITY', 'label': 'Security'}],
        'summary': 'good',
        'supplier_case_studies': [],
        'twitter_url': 'http://www.twitter.com',
        'verified_with_code': True,
        'verified_with_companies_house_oauth2': False,
        'verified_with_preverified_enrolment': False,
        'website': 'http://example.com',
    }
    actual = helpers.get_company_profile_from_response(response)

    assert actual == expected


def test_get_public_company_profile_from_response(
    api_response_company_profile_200, settings
):
    settings.SUPPLIER_PROFILE_URL = 'http://profile.com/{number}'
    response = api_response_company_profile_200
    expected = {
        'address_line_1': '123 Fake Street',
        'address_line_2': 'Fakeville',
        'country': 'GB',
        'date_of_creation': datetime(2015, 3, 2),
        'description': 'Ecommerce website',
        'email_address': 'test@example.com',
        'email_full_name': 'Jeremy',
        'employees': '501-1,000',
        'facebook_url': 'http://www.facebook.com',
        'has_valid_address': True,
        'is_published': True,
        'is_verification_letter_sent': False,
        'is_verified': True,
        'keywords': ['word1', 'word2'],
        'linkedin_url': 'http://www.linkedin.com',
        'locality': 'London',
        'logo': 'nice.jpg',
        'mobile_number': '07507694377',
        'modified': datetime(2016, 11, 23, 11, 21, 10, 977518),
        'name': 'Great company',
        'number': 123456,
        'po_box': '',
        'postal_code': 'E14 6XK',
        'postal_full_name': 'Jeremy',
        'public_profile_url': 'http://profile.com/123456',
        'sectors': [{'value': 'SECURITY', 'label': 'Security'}],
        'summary': 'good',
        'supplier_case_studies': [],
        'twitter_url': 'http://www.twitter.com',
        'verified_with_code': True,
        'verified_with_companies_house_oauth2': False,
        'verified_with_preverified_enrolment': False,
        'website': 'http://example.com',
    }
    actual = helpers.get_public_company_profile_from_response(response)
    assert actual == expected


def test_get_company_list_from_response(api_response_list_public_profile_200,
                                        settings):
    settings.SUPPLIER_PROFILE_URL = 'http://profile.com/{number}'
    response = api_response_list_public_profile_200
    expected = {
        'count': 20,
        'results': [
            {
                'address_line_1': '123 Fake Street',
                'address_line_2': 'Fakeville',
                'country': 'GB',
                'date_of_creation': datetime(2015, 3, 2),
                'description': 'Ecommerce website',
                'email_address': 'test@example.com',
                'email_full_name': 'Jeremy',
                'employees': '501-1,000',
                'facebook_url': 'http://www.facebook.com',
                'has_valid_address': True,
                'is_published': True,
                'is_verified': True,
                'is_verification_letter_sent': False,
                'keywords': ['word1', 'word2'],
                'linkedin_url': 'http://www.linkedin.com',
                'locality': 'London',
                'logo': 'nice.jpg',
                'mobile_number': '07507694377',
                'modified': datetime(2016, 11, 23, 11, 21, 10, 977518),
                'name': 'Great company',
                'number': 123456,
                'po_box': '',
                'postal_code': 'E14 6XK',
                'postal_full_name': 'Jeremy',
                'public_profile_url': 'http://profile.com/123456',
                'sectors': [{'value': 'SECURITY', 'label': 'Security'}],
                'summary': 'good',
                'supplier_case_studies': [],
                'twitter_url': 'http://www.twitter.com',
                'verified_with_code': True,
                'verified_with_companies_house_oauth2': False,
                'verified_with_preverified_enrolment': False,
                'website': 'http://example.com',
            }
        ],
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
