import http
from unittest.mock import patch

from requests import Response
import requests_mock


from enrolment import helpers


def profile_api_404(*args, **kwargs):
    response = Response()
    response.status_code = http.client.NOT_FOUND
    return response


@patch.object(helpers.api_client.supplier, 'retrieve_profile')
def test_has_company_no_company(mock_retrieve_supplier_profile):
    mock_response = Response()
    mock_response.status_code = http.client.OK
    mock_response.json = lambda: {
        'company': '',
    }
    mock_retrieve_supplier_profile.return_value = mock_response

    assert helpers.has_company(sso_session_id=123) is False


@patch.object(helpers.api_client.supplier, 'retrieve_profile', profile_api_404)
def test_has_company_404():
    assert helpers.has_company(sso_session_id=134) is False


def test_companies_house_client_consumes_auth(settings):
    helpers.CompaniesHouseClient.api_key = 'ff'
    with requests_mock.mock() as mock:
        mock.get('https://thing.com')
        response = helpers.CompaniesHouseClient.get('https://thing.com')
    expected = 'Basic ZmY6'  # base64 encoded ff
    assert response.request.headers['Authorization'] == expected


def test_verify_oauth2_code():
    with requests_mock.mock() as mock:
        mock.post(
            'https://account.companieshouse.gov.uk/oauth2/token',
            status_code=http.client.OK,
        )
        response = helpers.CompaniesHouseClient.verify_oauth2_code(
            code='123',
            redirect_uri='http://redirect.com',
        )
        assert response.status_code == 200

    request = mock.request_history[0]
    assert request.url == (
        'https://account.companieshouse.gov.uk/oauth2/token'
        '?grant_type=authorization_code'
        '&code=123'
        '&client_id=debug'
        '&client_secret=debug'
        '&redirect_uri=http%3A%2F%2Fredirect.com'
    )
