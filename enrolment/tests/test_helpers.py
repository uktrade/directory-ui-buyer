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


@patch.object(helpers.api_client.user, 'retrieve_profile')
def test_user_has_verified_company_no_company(mock_retrieve_user_profile):
    mock_response = Response()
    mock_response.status_code = http.client.OK
    mock_response.json = lambda: {
        'company': '',
        'company_email_confirmed': False,
    }
    mock_retrieve_user_profile.return_value = mock_response

    assert helpers.user_has_verified_company(sso_user_id=1) is False


@patch.object(helpers.api_client.user, 'retrieve_profile')
def test_user_has_verified_company_unconfirmed(mock_retrieve_user_profile):
    mock_response = Response()
    mock_response.status_code = http.client.OK
    mock_response.json = lambda: {
        'company': 'Extreme Corp',
        'company_email_confirmed': False,
    }
    mock_retrieve_user_profile.return_value = mock_response

    assert helpers.user_has_verified_company(sso_user_id=1) is False


@patch.object(helpers.api_client.user, 'retrieve_profile')
def test_user_has_verified_company(mock_retrieve_user_profile):
    mock_response = Response()
    mock_response.status_code = http.client.OK
    mock_response.json = lambda: {
        'company': 'Extreme Corp',
        'company_email_confirmed': True,
    }
    mock_retrieve_user_profile.return_value = mock_response

    assert helpers.user_has_verified_company(sso_user_id=1) is True


@patch.object(helpers.api_client.user, 'retrieve_profile', profile_api_404)
def test_user_has_verified_company_404():
    assert helpers.user_has_verified_company(sso_user_id=1) is False


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


@patch.object(helpers, 'get_companies_house_profile')
def test_cache_company_details_saves_in_session(
    mock_get_companies_house_profile, client
):
    data = {
        'date_of_creation': '2000-10-10',
        'company_name': 'Example corp',
        'company_status': 'active',
    }
    response = Response()
    response.status_code = http.client.OK
    response.json = lambda: data
    session = client.session
    mock_get_companies_house_profile.return_value = response

    helpers.cache_company_details(session, '01234567')

    mock_get_companies_house_profile.assert_called_once_with(number='01234567')
    assert session[helpers.COMPANIES_HOUSE_PROFILE_SESSION_KEY] == data
    assert session.modified is True


@patch.object(helpers, 'get_companies_house_profile')
def test_cache_company_details_handles_bad_response(
    mock_get_companies_house_profile, client
):
    response = Response()
    response.status_code = http.client.BAD_REQUEST

    session = client.session
    mock_get_companies_house_profile.return_value = response

    with pytest.raises(HTTPError):
        helpers.cache_company_details(session, '01234567')


def test_companies_house_client_consumes_auth(settings):
    settings.COMPANIES_HOUSE_API_KEY = 'ff'
    with requests_mock.mock() as mock:
        mock.get('https://thing.com')
        response = helpers.companies_house_client('https://thing.com')
    expected = 'Basic ZmY6'  # base64 encoded ff
    assert response.request.headers['Authorization'] == expected


def test_companies_house_client_logs_unauth(caplog):
    with requests_mock.mock() as mock:
        mock.get(
            'https://thing.com',
            status_code=http.client.UNAUTHORIZED,
        )
        helpers.companies_house_client('https://thing.com')
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
        response = helpers.get_companies_house_profile('01234567')
    assert response.json() == profile


def test_get_cached_company_date_of_creation(client):
    session = client.session
    key = helpers.COMPANIES_HOUSE_PROFILE_SESSION_KEY
    session[key] = {'date_of_creation': '2000-10-10'}

    assert helpers.get_cached_company_date_of_creation(session) == '2000-10-10'


def test_get_cached_company_name(client):
    session = client.session
    key = helpers.COMPANIES_HOUSE_PROFILE_SESSION_KEY
    session[key] = {'company_name': 'Example corp'}

    assert helpers.get_cached_company_name(session) == 'Example corp'


def test_get_cached_company_status(client):
    session = client.session
    key = helpers.COMPANIES_HOUSE_PROFILE_SESSION_KEY
    session[key] = {'company_status': 'active'}

    assert helpers.get_cached_company_status(session) == 'active'
