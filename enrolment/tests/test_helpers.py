import http
from unittest.mock import patch

from requests import Response
from requests.exceptions import HTTPError, ConnectionError, SSLError, Timeout

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


@patch.object(helpers.api_client.company, 'retrieve_companies_house_profile',)
def test_get_company_name_handles_exception(
        mock_retrieve_companies_house_profile, caplog):
    exceptions = [HTTPError, ConnectionError, SSLError, Timeout]
    for exception in exceptions:
        mock_retrieve_companies_house_profile.side_effect = exception('!')
        response = helpers.get_company_name('01234567')
        log = caplog.records[0]
        assert response is None
        assert log.levelname == 'ERROR'
        assert log.msg == 'Unable to get name for "01234567".'


@patch.object(helpers.api_client.company, 'retrieve_companies_house_profile',)
def test_get_company_name_handles_bad_status(
        mock_retrieve_companies_house_profile, caplog):

    mock_response = Response()
    mock_response.status_code = http.client.BAD_REQUEST
    mock_retrieve_companies_house_profile.return_value = mock_response

    name = helpers.get_company_name('01234567')
    log = caplog.records[0]

    mock_retrieve_companies_house_profile.assert_called_once_with('01234567')
    assert name is None
    assert log.levelname == 'ERROR'
    assert log.msg == 'Unable to get name for "01234567". Status "400".'


@patch.object(helpers.api_client.company, 'retrieve_companies_house_profile',)
def test_get_company_name_handles_good_status(
        mock_retrieve_companies_house_profile, caplog):

    mock_response = Response()
    mock_response.status_code = http.client.OK
    mock_response.json = lambda: {'company_name': 'Extreme Corp'}
    mock_retrieve_companies_house_profile.return_value = mock_response

    name = helpers.get_company_name('01234567')

    mock_retrieve_companies_house_profile.assert_called_once_with('01234567')
    assert name == 'Extreme Corp'
