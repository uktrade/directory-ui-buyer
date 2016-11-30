import http
from unittest.mock import patch

import requests
import pytest


@pytest.fixture
def api_response_200():
    response = requests.Response()
    response.status_code = http.client.OK
    response.json = lambda: {}
    return response


@pytest.fixture
def api_response_list_public_profile_200(api_response_200):
    response = api_response_200
    response.json = lambda: {
        'results': [
            {
                'sectors': ['SECTOR1', 'SECTOR2'],
                'number': '123456',
                'name': 'UK exporting co ltd.',
                'description': 'Exporters of UK wares.',
                'website': 'http://www.ukexportersnow.co.uk',
                'logo': 'www.ukexportersnow.co.uk/logo.png',
                'keywords': 'word1 word2',
                'date_of_creation': '2015-03-01',
                'employees': '1001-10000',
                'supplier_case_studies': [],
            }
        ],
        'count': 20
    }
    return response


@pytest.fixture(autouse=True)
def retrieve_supplier_case_study_response(api_response_200):
    stub = patch(
        'api_client.api_client.company.retrieve_supplier_case_study',
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
