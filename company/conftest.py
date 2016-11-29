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


@pytest.fixture(autouse=True)
def retrieve_supplier_case_study_response(api_response_200):
    stub = patch(
        'api_client.api_client.company.retrieve_supplier_case_study',
        return_value=api_response_200,
    )
    stub.start()
    yield
    stub.stop()
