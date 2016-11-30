import requests
import pytest

from company import helpers


@pytest.fixture
def profile_data():
    return {
        'website': 'http://www.example.com',
        'description': 'bloody good',
        'number': '01234567',
        'date_of_creation': '2010-10-10',
        'sectors': ['AGRICULTURE_HORTICULTURE_AND_FISHERIES'],
        'logo': 'nice.png',
        'name': 'Great corp',
        'keywords': 'hello, hi',
        'employees': '1001-10000',
        'supplier_case_studies': [],
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
        'number': '01234567',
        'date_of_creation': '10 Oct 2010',
        'sectors': [
            {
                'label': 'Agriculture, horticulture and fisheries',
                'value': 'AGRICULTURE_HORTICULTURE_AND_FISHERIES',
            }
        ],
        'logo': 'nice.png',
        'name': 'Great corp',
        'keywords': 'hello, hi',
        'employees': '1,001-10,000',
        'supplier_case_studies': []
    }
    actual = helpers.get_company_profile_from_response(response)
    assert actual == expected


def test_get_public_company_profile_from_response(profile_data):
    response = requests.Response()
    response.json = lambda: profile_data
    expected = {
        'website': 'http://www.example.com',
        'description': 'bloody good',
        'number': '01234567',
        'date_of_creation': '10 Oct 2010',
        'sectors': [
            {
                'label': 'Agriculture, horticulture and fisheries',
                'value': 'AGRICULTURE_HORTICULTURE_AND_FISHERIES',
            }
        ],
        'logo': 'nice.png',
        'name': 'Great corp',
        'keywords': 'hello, hi',
        'employees': '1,001-10,000',
        'supplier_case_studies': []
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
                'number': '01234567',
                'date_of_creation': '10 Oct 2010',
                'sectors': [
                    {
                        'label': 'Agriculture, horticulture and fisheries',
                        'value': 'AGRICULTURE_HORTICULTURE_AND_FISHERIES',
                    }
                ],
                'logo': 'nice.png',
                'name': 'Great corp',
                'keywords': 'hello, hi',
                'employees': '1,001-10,000',
                'supplier_case_studies': [],
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
        ['2010-10-10', '10 Oct 2010'],
        ['', ''],
        [None, None],
    ]
    for provided, expected in pairs:
        assert helpers.format_date_of_creation(provided) == expected
