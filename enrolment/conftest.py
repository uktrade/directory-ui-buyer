import http
from unittest.mock import patch

from directory_api_client.client import api_client
import requests
import pytest


@pytest.fixture
def api_response_200():
    response = requests.Response()
    response.status_code = http.client.OK
    response.json = lambda: {}
    return response


@pytest.fixture(autouse=True)
def company_unique_api_response(api_response_200):
    stub = patch.object(
        api_client.company, 'validate_company_number',
        return_value=api_response_200,
    )
    stub.start()
    yield
    stub.stop()
