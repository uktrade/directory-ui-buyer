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


def test_get_employees_label():
    assert helpers.get_employees_label('1001-10000') == '1,001-10,000'


def test_get_sectors_labels():
    values = ['AGRICULTURE_HORTICULTURE_AND_FISHERIES', 'AEROSPACE']
    expected = ['Agriculture, horticulture and fisheries', 'Aerospace']
    assert helpers.get_sectors_labels(values) == expected


def test_get_employees_label_none():
    assert helpers.get_employees_label('') == ''


def test_get_sectors_labels_none():
    assert helpers.get_sectors_labels([]) == []


def test_inflate_company_profile_from_response(profile_data):
    response = requests.Response()
    response.json = lambda: profile_data
    expected = {
        'website': 'http://www.example.com',
        'description': 'bloody good',
        'number': '01234567',
        'date_of_creation': '10 Oct 2010',
        'sectors': ['Agriculture, horticulture and fisheries'],
        'logo': 'nice.png',
        'name': 'Great corp',
        'keywords': 'hello, hi',
        'employees': '1,001-10,000',
        'supplier_case_studies': []
    }
    actual = helpers.inflate_company_profile_from_response(response)
    assert actual == expected


def test_inflate_company_profile_from_response_without_date(profile_data):
    pairs = [
        ['2010-10-10', '10 Oct 2010'],
        ['', ''],
        [None, None],
    ]
    for provided, expected in pairs:
        assert helpers.format_date_of_creation(provided) == expected
