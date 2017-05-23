import http
from unittest.mock import patch

import pytest
from requests import Response
from requests.exceptions import HTTPError
import requests_mock

from django import forms

from enrolment import helpers


def mock_validator_one(value):
    raise forms.ValidationError('error one')


def mock_validator_two(value):
    raise forms.ValidationError('error two')


class MockForm(forms.Form):
    field = forms.CharField(
        validators=[mock_validator_one, mock_validator_two],
    )


class MockHaltingValidatorForm(forms.Form):
    field = forms.CharField(
        validators=helpers.halt_validation_on_failure(
            mock_validator_one, mock_validator_two,
        )
    )


def profile_api_400(*args, **kwargs):
    response = Response()
    response.status_code = http.client.BAD_REQUEST
    return response


def profile_api_404(*args, **kwargs):
    response = Response()
    response.status_code = http.client.NOT_FOUND
    return response


def test_validator_raises_all():
    form = MockForm({'field': 'value'})
    assert form.is_valid() is False
    assert 'error one' in form.errors['field']
    assert 'error two' in form.errors['field']


def test_halt_validation_on_failure_raises_first():
    form = MockHaltingValidatorForm({'field': 'value'})
    assert form.is_valid() is False
    assert 'error one' in form.errors['field']
    assert 'error two' not in form.errors['field']


@patch.object(helpers.api_client.supplier, 'retrieve_profile')
def test_has_company_no_company(mock_retrieve_supplier_profile):
    mock_response = Response()
    mock_response.status_code = http.client.OK
    mock_response.json = lambda: {
        'company': '',
    }
    mock_retrieve_supplier_profile.return_value = mock_response

    assert helpers.has_company(sso_user_id=1) is False


@patch.object(helpers.api_client.supplier, 'retrieve_profile', profile_api_404)
def test_has_company_404():
    assert helpers.has_company(sso_user_id=1) is False


@patch.object(helpers.CompaniesHouseClient, 'retrieve_profile')
def test_store_companies_house_profile_in_session_saves_in_session(
    mock_retrieve_profile, client
):
    data = {
        'date_of_creation': '2000-10-10',
        'company_name': 'Example corp',
        'company_status': 'active',
        'registered_office_address': {'foo': 'bar'}
    }
    response = Response()
    response.status_code = http.client.OK
    response.json = lambda: data
    session = client.session
    mock_retrieve_profile.return_value = response

    helpers.store_companies_house_profile_in_session(session, '01234567')

    mock_retrieve_profile.assert_called_once_with(number='01234567')
    assert session[helpers.COMPANIES_HOUSE_PROFILE_SESSION_KEY] == data
    assert session.modified is True


@patch.object(helpers.CompaniesHouseClient, 'retrieve_profile')
def test_store_companies_house_profile_in_session_handles_bad_response(
    mock_retrieve_profile, client
):
    response = Response()
    response.status_code = http.client.BAD_REQUEST

    session = client.session
    mock_retrieve_profile.return_value = response

    with pytest.raises(HTTPError):
        helpers.store_companies_house_profile_in_session(session, '01234567')


def test_companies_house_client_consumes_auth(settings):
    helpers.CompaniesHouseClient.api_key = 'ff'
    with requests_mock.mock() as mock:
        mock.get('https://thing.com')
        response = helpers.CompaniesHouseClient.get('https://thing.com')
    expected = 'Basic ZmY6'  # base64 encoded ff
    assert response.request.headers['Authorization'] == expected


def test_companies_house_client_logs_unauth(caplog):
    with requests_mock.mock() as mock:
        mock.get(
            'https://thing.com',
            status_code=http.client.UNAUTHORIZED,
        )
        helpers.CompaniesHouseClient.get('https://thing.com')
    log = caplog.records[0]
    assert log.levelname == 'ERROR'
    assert log.msg == helpers.MESSAGE_AUTH_FAILED


def test_get_companies_house_profile():
    profile = {'company_status': 'active'}
    with requests_mock.mock() as mock:
        mock.get(
            'https://api.companieshouse.gov.uk/company/01234567',
            status_code=http.client.OK,
            json=profile
        )
        response = helpers.CompaniesHouseClient.retrieve_profile('01234567')
    assert response.json() == profile


def test_get_companies_house_contact_details():
    contact_details = {'address': '111!'}
    with requests_mock.mock() as mock:
        mock.get(
            ('https://api.companieshouse.gov.uk/company/01234567/'
             'registered-office-address'),
            status_code=http.client.OK,
            json=contact_details
        )
        response = helpers.CompaniesHouseClient.retrieve_address('01234567')
    assert response.json() == contact_details


def test_get_company_date_of_creation_from_session(client):
    session = client.session
    key = helpers.COMPANIES_HOUSE_PROFILE_SESSION_KEY
    session[key] = {'company': {'date_of_creation': '2000-10-10'}}

    actual = helpers.get_company_date_of_creation_from_session(session)

    assert actual == '2000-10-10'


def test_get_company_name_from_session(client):
    session = client.session
    key = helpers.COMPANIES_HOUSE_PROFILE_SESSION_KEY
    session[key] = {'company': {'company_name': 'Example corp'}}

    assert helpers.get_company_name_from_session(session) == 'Example corp'


def test_get_company_status_from_session(client):
    session = client.session
    key = helpers.COMPANIES_HOUSE_PROFILE_SESSION_KEY
    session[key] = {'company': {'company_status': 'active'}}

    assert helpers.get_company_status_from_session(session) == 'active'
