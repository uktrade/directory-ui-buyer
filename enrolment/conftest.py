import http
from unittest.mock import patch, Mock

import pytest


@pytest.fixture(autouse=True)
def company_unique_api_response():
    stub = patch(
        'api_client.api_client.company.validate_company_number',
        return_value=Mock(status_code=http.client.OK)
    )
    stub.start()
    yield
    stub.stop()
