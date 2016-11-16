import http
from unittest.mock import patch

import pytest
from requests import exceptions, Response

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


@patch.object(helpers.api_client.company, 'retrieve_companies_house_profile')
def test_get_company_name_handles_bad_status(
    mock_retrieve_companies_house_profile
):
    mock_retrieve_companies_house_profile.return_value = profile_api_400()

    with pytest.raises(exceptions.HTTPError):
        helpers.get_company_name('01234567')


@patch.object(helpers.api_client.company, 'retrieve_companies_house_profile',)
def test_get_company_name_handles_good_status(
    mock_retrieve_companies_house_profile
):

    mock_response = Response()
    mock_response.status_code = http.client.OK
    mock_response.json = lambda: {'company_name': 'Extreme Corp'}
    mock_retrieve_companies_house_profile.return_value = mock_response

    name = helpers.get_company_name('01234567')

    mock_retrieve_companies_house_profile.assert_called_once_with('01234567')
    assert name == 'Extreme Corp'


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
