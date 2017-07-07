from copy import deepcopy
import http
from unittest.mock import patch

import requests
import pytest


@pytest.fixture
def retrieve_profile_data():
    return {
        'address_line_1': '123 Fake Street',
        'address_line_2': 'Fakeville',
        'country': 'GB',
        'date_of_creation': '2015-03-02',
        'description': 'Ecommerce website',
        'email_address': 'test@example.com',
        'email_full_name': 'Jeremy',
        'employees': '501-1000',
        'facebook_url': 'http://www.facebook.com',
        'has_valid_address': True,
        'is_published': True,
        'is_verification_letter_sent': False,
        'keywords': 'word1, word2',
        'linkedin_url': 'http://www.linkedin.com',
        'locality': 'London',
        'logo': 'nice.jpg',
        'mobile_number': '07507694377',
        'modified': '2016-11-23T11:21:10.977518Z',
        'name': 'Great company',
        'number': 123456,
        'po_box': '',
        'postal_code': 'E14 6XK',
        'postal_full_name': 'Jeremy',
        'sectors': ['SECURITY'],
        'summary': 'good',
        'supplier_case_studies': [],
        'twitter_url': 'http://www.twitter.com',
        'verified_with_code': True,
        'verified_with_preverified_enrolment': False,
        'website': 'http://example.com',
    }


@pytest.fixture
def list_public_profiles_data(retrieve_profile_data):
    return {
        'results': [
            retrieve_profile_data
        ],
        'count': 20
    }


@pytest.fixture
def supplier_case_study_data(retrieve_profile_data):
    return {
        'description': 'Damn great',
        'sector': 'SOFTWARE_AND_COMPUTER_SERVICES',
        'image_three': 'https://image_three.jpg',
        'website': 'http://www.google.com',
        'video_one': 'https://video_one.wav',
        'title': 'Two',
        'company': retrieve_profile_data,
        'image_one': 'https://image_one.jpg',
        'testimonial': 'I found it most pleasing.',
        'keywords': 'great',
        'pk': 2,
        'year': '2000',
        'image_two': 'https://image_two.jpg'
    }


@pytest.fixture
def company_profile_companies_house_data():
    return {
        'email_full_name': 'Jeremy Companies House',
        'email_address': 'test@example.com',
        'postal_full_name': 'Jeremy',
        'address_line_1': '123 Fake Street',
        'address_line_2': 'Fakeville',
        'locality': 'London',
        'postal_code': 'E14 6XK',
        'po_box': '',
        'country': 'GB',
    }


@pytest.fixture
def api_response_company_profile_companies_house_200(
    company_profile_companies_house_data
):
    response = requests.Response()
    response.status_code = http.client.OK
    response.json = lambda: deepcopy(company_profile_companies_house_data)
    return response


@pytest.fixture
def api_response_company_profile_200(retrieve_profile_data):
    response = requests.Response()
    response.status_code = http.client.OK
    response.json = lambda: deepcopy(retrieve_profile_data)
    return response


@pytest.fixture
def api_response_company_profile_letter_sent_200(retrieve_profile_data):
    profile_data = deepcopy(retrieve_profile_data)
    profile_data['is_verification_letter_sent'] = True
    response = requests.Response()
    response.status_code = http.client.OK
    response.json = lambda: profile_data
    return response


@pytest.fixture
def api_response_company_profile_no_contact_details(retrieve_profile_data):
    data = retrieve_profile_data.copy()
    data['has_valid_address'] = False
    response = requests.Response()
    response.status_code = http.client.OK
    response.json = lambda: deepcopy(data)
    return response


@pytest.fixture
def api_response_200():
    response = requests.Response()
    response.status_code = http.client.OK
    response.json = lambda: deepcopy({})
    return response


@pytest.fixture
def api_response_list_public_profile_200(
    api_response_200, list_public_profiles_data
):
    response = api_response_200
    response.json = lambda: deepcopy(list_public_profiles_data)
    return response


@pytest.fixture
def api_response_retrieve_supplier_case_study_200(supplier_case_study_data):
    response = api_response_200()
    response.json = lambda: deepcopy(supplier_case_study_data)
    return response


@pytest.fixture(autouse=True)
def retrieve_supplier_case_study_response(api_response_200):
    stub = patch(
        'api_client.api_client.company.retrieve_private_case_study',
        return_value=api_response_200,
    )
    stub.start()
    yield
    stub.stop()


@pytest.fixture(autouse=True)
def list_public_profiles(api_response_list_public_profile_200):
    stub = patch(
        'api_client.api_client.company.list_public_profiles',
        return_value=api_response_list_public_profile_200,
    )
    stub.start()
    yield
    stub.stop()


@pytest.fixture(autouse=True)
def retrieve_supplier_case_study(
    api_response_retrieve_supplier_case_study_200
):
    stub = patch(
        'api_client.api_client.company.retrieve_private_case_study',
        return_value=api_response_retrieve_supplier_case_study_200,
    )
    stub.start()
    yield
    stub.stop()


@pytest.fixture(autouse=True)
def retrieve_profile(api_response_company_profile_200):
    stub = patch(
        'api_client.api_client.company.retrieve_private_profile',
        return_value=api_response_company_profile_200,
    )
    stub.start()
    yield
    stub.stop()


@pytest.fixture(autouse=True)
def get_companies_house_office_address(
    api_response_company_profile_companies_house_200
):
    stub = patch(
        'company.helpers.CompaniesHouseClient.retrieve_address',
        return_value=api_response_company_profile_companies_house_200,
    )
    stub.start()
    yield
    stub.stop()
