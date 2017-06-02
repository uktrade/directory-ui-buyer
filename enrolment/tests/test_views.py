import http
from unittest.mock import patch, Mock
import re

from django.core.urlresolvers import reverse
from django.forms import ValidationError

import requests
from requests.exceptions import RequestException, HTTPError
import pytest

from enrolment import helpers
from enrolment.validators import (
    MESSAGE_COMPANY_NOT_ACTIVE,
    MESSAGE_COMPANY_NOT_FOUND,
    MESSAGE_COMPANY_ERROR
)
from enrolment.views import (
    api_client,
    EnrolmentView,
    SubmitEnrolmentView
)
from sso.utils import SSOUser


MOCK_COMPANIES_HOUSE_API_COMPANY_PROFILE = {
    'company_name': 'company_name',
    'company_status': 'active',
    'date_of_creation': 'date_of_creation',
    'company_number': '12345678',
    'registered_office_address': {
        'address_line_1': 'address_line_1',
        'address_line_2': 'address_line_2',
        'care_of': 'care_of',
        'country': 'country',
        'locality': 'locality',
        'po_box': 'po_box',
        'postal_code': 'postal_code',
        'premises': 'premises',
        'region': 'region'
    }
}


@pytest.fixture
def sso_user():
    return SSOUser(
        id=1,
        email='jim@example.com',
    )


def process_request(self, request):
    request.sso_user = sso_user()


def process_request_anon(self, request):
    request.sso_user = None


@pytest.fixture
def buyer_form_data():
    return {
        'full_name': 'Jim Example',
        'email_address': 'jim@example.com',
        'sector': 'AEROSPACE',
        'terms': True
    }


@pytest.fixture
def buyer_request(rf, client, buyer_form_data):
    request = rf.post('/', buyer_form_data)
    request.session = client.session
    return request


@pytest.fixture
def anon_request(rf, client):
    request = rf.get('/')
    request.sso_user = None
    request.session = client.session
    return request


@pytest.fixture
def company_request(rf, client, sso_user):
    request = rf.get('/')
    request.sso_user = sso_user
    request.session = client.session
    return request


@pytest.fixture
def sso_request(company_request, sso_user):
    request = company_request
    request.sso_user = sso_user
    return request


@pytest.fixture
def api_response_200(*args, **kwargs):
    response = requests.Response()
    response.status_code = http.client.OK
    return response


@pytest.fixture
def api_response_companies_house_search_200(api_response_200):
    payload = {
        'items': [{'name': 'Smashing corp'}]
    }
    api_response_200.json = lambda: payload
    return api_response_200


@pytest.fixture
def api_response_400(*args, **kwargs):
    response = requests.Response()
    response.status_code = http.client.BAD_REQUEST
    return response


@pytest.fixture
def api_response_validate_company_number_400(api_response_400):
    api_response_400.json = lambda: {'number': ['Not good']}
    return api_response_400


@pytest.fixture
def api_response_company_profile_no_sectors_200(api_response_200):
    response = api_response_200
    payload = {
        'website': 'http://example.com',
        'description': 'Ecommerce website',
        'number': 123456,
        'sectors': None,
        'logo': 'nice.jpg',
        'name': 'Great company',
        'keywords': 'word1 word2',
        'employees': '501-1000',
        'date_of_creation': '2015-03-02',
    }
    response.json = lambda: payload
    return response


@pytest.fixture
def api_response_company_profile_no_date_of_creation_200(api_response_200):
    response = api_response_200
    payload = {
        'website': 'http://example.com',
        'description': 'Ecommerce website',
        'number': 123456,
        'sectors': None,
        'logo': 'nice.jpg',
        'name': 'Great company',
        'keywords': 'word1 word2',
        'employees': '501-1000',
        'date_of_creation': None,
    }
    response.json = lambda: payload
    return response


@patch(
    'enrolment.helpers.get_company_from_companies_house',
    Mock(return_value=MOCK_COMPANIES_HOUSE_API_COMPANY_PROFILE)
)
@patch('enrolment.helpers.has_company', Mock(return_value=False))
@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch.object(api_client.registration, 'send_form', api_response_200)
def test_submit_enrolment_api_client_success(client):
    response = client.get(
        reverse('register-submit'),
        {
            'company_number': '12345678',
            'export_status': 'ONE_TWO_YEARS_AGO'
        }
    )
    assert response.template_name == SubmitEnrolmentView.success_template


@patch(
    'enrolment.helpers.get_company_from_companies_house',
    Mock(return_value=MOCK_COMPANIES_HOUSE_API_COMPANY_PROFILE)
)
@patch('enrolment.helpers.has_company', Mock(return_value=False))
@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch.object(api_client.registration, 'send_form', api_response_400)
def test_submit_enrolment_api_client_fail(client):
    response = client.get(
        reverse('register-submit'),
        {
            'company_number': '12345678',
            'export_status': 'ONE_TWO_YEARS_AGO'
        }
    )
    assert response.template_name == SubmitEnrolmentView.failure_template


@patch(
    'enrolment.helpers.get_company_from_companies_house',
    Mock(return_value=MOCK_COMPANIES_HOUSE_API_COMPANY_PROFILE)
)
@patch('enrolment.helpers.has_company', Mock(return_value=False))
@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
def test_enrolment_views_use_correct_template(client):
    for step_name, form in EnrolmentView.form_list:

        query_params = {}
        if step_name == 'company':
            query_params = {'company_number': 12345678}

        response = client.get(
            reverse('register', kwargs={'step': step_name}),
            query_params
        )

        assert response.template_name == [EnrolmentView.templates[step_name]]


@patch('enrolment.helpers.has_company', return_value=True)
@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
def test_enrolment_logged_in_has_company_redirects(
    mock_has_company, client, sso_user
):
    url = reverse('register', kwargs={'step': EnrolmentView.COMPANY})
    response = client.get(url)

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == reverse('company-detail')
    mock_has_company.assert_called_once_with(sso_user.id)


@patch('enrolment.helpers.has_company', return_value=False)
@patch('sso.middleware.SSOUserMiddleware.process_request',
       process_request_anon)
def test_submit_enrolment_logged_out_has_company_redirects(
    mock_has_company, client
):
    url = reverse('register-submit')
    response = client.get(url)

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == (
         'http://sso.trade.great.dev:8004/accounts/signup/'
         '?next=http%3A//testserver/register-submit'
    )
    mock_has_company.assert_not_called()


def test_companies_house_search_validation_error(client):
    url = reverse('api-internal-companies-house-search')
    response = client.get(url)  # notice absense of `term`

    assert response.status_code == 400


@patch('enrolment.helpers.CompaniesHouseClient.search')
def test_companies_house_search_api_error(
    mock_search, client, api_response_400
):
    mock_search.return_value = api_response_400
    url = reverse('api-internal-companies-house-search')

    with pytest.raises(requests.exceptions.HTTPError):
        client.get(url, data={'term': 'thing'})


@patch('enrolment.helpers.CompaniesHouseClient.search')
def test_companies_house_search_api_success(
    mock_search, client, api_response_companies_house_search_200
):
    mock_search.return_value = api_response_companies_house_search_200
    url = reverse('api-internal-companies-house-search')

    response = client.get(url, data={'term': 'thing'})

    assert response.status_code == 200
    assert response.content == b'[{"name": "Smashing corp"}]'


@patch('sso.middleware.SSOUserMiddleware.process_request',
       process_request_anon)
def test_landing_page_context_no_sso_user(client):
    response = client.get(reverse('index'))

    assert response.context_data['user_has_company'] is None


@patch(
    'sso.middleware.SSOUserMiddleware.process_request',
    process_request_anon
)
def test_landing_page_buyers_waiting_number(settings, client):
    settings.BUYERS_WAITING_NUMBER = '1,000,000,000'
    response = client.get(reverse('index'))

    assert re.search(
        settings.BUYERS_WAITING_NUMBER + r'.*buyers are waiting for you',
        str(response.content)
    )


@patch('enrolment.helpers.has_company', Mock(return_value=False))
@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
def test_landing_page_context_sso_user_without_company(client):
    response = client.get(reverse('index'))

    assert response.context_data['user_has_company'] is False


@patch('enrolment.helpers.has_company', Mock(return_value=True))
@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
def test_landing_page_context_sso_user_with_company(client):
    response = client.get(reverse('index'))

    assert response.context_data['user_has_company'] is True


@patch('api_client.api_client.company.validate_company_number')
def test_landing_page_submit_invalid_form_shows_errors(
    mock_company_unique, settings, client,
    api_response_validate_company_number_400
):
    mock_company_unique.return_value = api_response_validate_company_number_400

    url = reverse('index')
    params = {'company_number': '11111111'}
    response = client.post(url, params)

    assert response.status_code == 200
    assert response.context['form'].errors == {'company_number': ['Not good']}


@patch(
    'enrolment.helpers.get_company_from_companies_house',
    Mock(return_value={
        'company_name': 'company_name',
        'company_status': 'inactive',
        'date_of_creation': 'date_of_creation',
        'company_number': '12345678',
        'registered_office_address': {
            'address_line_1': 'address_line_1',
            'address_line_2': 'address_line_2',
            'care_of': 'care_of',
            'country': 'country',
            'locality': 'locality',
            'po_box': 'po_box',
            'postal_code': 'postal_code',
            'premises': 'premises',
            'region': 'region'
        }
    })
)
@patch('enrolment.helpers.has_company', Mock(return_value=False))
@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
def test_landing_page_submit_company_not_active(client):
    url = reverse('index')
    params = {'company_number': '12345678'}
    response = client.post(url, params)

    assert response.context['form'].errors == {
        'company_number': [MESSAGE_COMPANY_NOT_ACTIVE]
    }


@patch(
    'enrolment.helpers.get_company_from_companies_house',
    Mock(side_effect=HTTPError(
        response=Mock(status_code=http.client.INTERNAL_SERVER_ERROR))
    )
)
@patch('enrolment.helpers.has_company', Mock(return_value=False))
@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
def test_landing_page_submit_companies_house_server_error(client):
    url = reverse('index')
    params = {'company_number': '12345678'}
    response = client.post(url, params)

    assert response.context['form'].errors == {
        'company_number': [MESSAGE_COMPANY_ERROR]
    }


@patch(
    'enrolment.helpers.get_company_from_companies_house',
    Mock(side_effect=HTTPError(
        response=Mock(status_code=http.client.NOT_FOUND))
    )
)
@patch('enrolment.helpers.has_company', Mock(return_value=False))
@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
def test_landing_page_submit_company_not_found(client):
    url = reverse('index')
    params = {'company_number': '12345678'}
    response = client.post(url, params)

    assert response.context['form'].errors == {
        'company_number': [MESSAGE_COMPANY_NOT_FOUND]
    }


@patch(
    'enrolment.helpers.get_company_from_companies_house',
    Mock(return_value=MOCK_COMPANIES_HOUSE_API_COMPANY_PROFILE)
)
def test_landing_page_submit_valid_form_redirects(client):
    url = reverse('index')
    params = {'company_number': '12345678'}
    response = client.post(url, params)

    expected_url = '/register/company?company_number=12345678'
    assert response.status_code == 302
    assert response.get('Location') == expected_url


@patch(
    'enrolment.helpers.get_company_from_companies_house',
    Mock(return_value=MOCK_COMPANIES_HOUSE_API_COMPANY_PROFILE)
)
@patch('enrolment.helpers.has_company', Mock(return_value=False))
@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
def test_company_enrolment_step_caches_profile(client):
    client.get(
        reverse('register', kwargs={'step': 'company'}),
        {'company_number': 12345678}
    )

    assert client.session[
        helpers.COMPANIES_HOUSE_PROFILE_SESSION_KEY
    ] == MOCK_COMPANIES_HOUSE_API_COMPANY_PROFILE


@patch('enrolment.helpers.has_company', Mock(return_value=False))
@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
def test_company_enrolment_step_handles_api_company_not_found(client):

    with patch('enrolment.helpers.get_company_from_companies_house') as mock:
        mock.side_effect = RequestException(
            response=Mock(status_code=http.client.NOT_FOUND),
            request=Mock(),
        )

        response = client.get(
            reverse('register', kwargs={'step': 'company'}),
            {'company_number': 12345678}
        )

    assert "Company not found" in str(response.content)


@patch('enrolment.helpers.has_company', Mock(return_value=False))
@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
def test_company_enrolment_step_handles_api_company_error(client):

    with patch('enrolment.helpers.get_company_from_companies_house') as mock:
        mock.side_effect = RequestException(
            response=Mock(status_code=500),
            request=Mock(),
        )

        response = client.get(
            reverse('register', kwargs={'step': 'company'}),
            {'company_number': 12345678}
        )
    assert 'Error. Please try again later.' in str(response.content)


@patch('enrolment.helpers.has_company', Mock(return_value=False))
@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch('enrolment.helpers.store_companies_house_profile_in_session', Mock())
def test_company_enrolment_step_company_number_not_provided(client):
    response = client.get(reverse('register', kwargs={'step': 'company'}))
    assert 'Company number not provided.' in str(response.content)


@patch('enrolment.helpers.has_company', Mock(return_value=False))
@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch('enrolment.helpers.store_companies_house_profile_in_session', Mock())
@patch('enrolment.helpers.get_company_status_from_session',
       Mock(return_value='active'))
@patch('enrolment.helpers.get_company_from_session',
       Mock(return_value=MOCK_COMPANIES_HOUSE_API_COMPANY_PROFILE))
@patch('enrolment.helpers.get_company_number_from_session')
def test_company_enrolment_step_company_number_in_session_cache(
        mock_get_company_number_from_session,
        client):

    mock_get_company_number_from_session.return_value = 12345678
    response = client.get(reverse('register', kwargs={'step': 'company'}))

    assert mock_get_company_number_from_session.called
    assert '12345678' in str(response.content)


@patch('enrolment.helpers.has_company', Mock(return_value=False))
@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch('enrolment.helpers.store_companies_house_profile_in_session', Mock())
@patch('enrolment.helpers.get_company_status_from_session',
       Mock(return_value='active'))
@patch('enrolment.helpers.get_company_from_session',
       Mock(return_value=MOCK_COMPANIES_HOUSE_API_COMPANY_PROFILE))
@patch('enrolment.helpers.get_company_number_from_session')
def test_company_enrolment_step_company_number_queryparam_and_session_cache(
        mock_get_company_number_from_session,
        client):

    mock_get_company_number_from_session.return_value = 87654321
    response = client.get(reverse('register', kwargs={'step': 'company'}),
                          {'company_number': 12345678})

    assert not mock_get_company_number_from_session.called
    assert '12345678' in str(response.content)


@patch('enrolment.helpers.has_company', Mock(return_value=False))
@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch('enrolment.helpers.store_companies_house_profile_in_session', Mock())
@patch('enrolment.helpers.get_company_status_from_session',
       Mock(return_value='not active'))
def test_company_enrolment_step_handles_company_not_active(client):

    with patch('enrolment.validators.company_active') as mock:
        mock.side_effect = ValidationError(MESSAGE_COMPANY_NOT_ACTIVE)

        response = client.get(
            reverse('register', kwargs={'step': 'company'}),
            {'company_number': 12345678}
        )

    assert MESSAGE_COMPANY_NOT_ACTIVE in str(response.content)


@patch('enrolment.helpers.has_company', Mock(return_value=False))
@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch('enrolment.helpers.store_companies_house_profile_in_session',
       Mock())
@patch('enrolment.helpers.get_company_status_from_session',
       Mock(return_value='active'))
def test_company_enrolment_step_handles_company_already_registered(client):

    with patch('enrolment.validators.company_unique') as mock:
        mock.side_effect = ValidationError('Company already exists')

        response = client.get(
            reverse('register', kwargs={'step': 'company'}),
            {'company_number': 12345678}
        )

    assert 'Company already exists' in str(response.content)


@patch(
    'enrolment.helpers.get_company_from_companies_house',
    Mock(return_value=MOCK_COMPANIES_HOUSE_API_COMPANY_PROFILE)
)
@patch('enrolment.helpers.has_company', Mock(return_value=False))
@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
def test_submit_enrolment_caches_profile(client):
    client.get(
        reverse('register-submit'),
        {
            'company_number': '12345678',
            'export_status': 'ONE_TWO_YEARS_AGO'
        }
    )

    assert client.session[
        helpers.COMPANIES_HOUSE_PROFILE_SESSION_KEY
    ] == MOCK_COMPANIES_HOUSE_API_COMPANY_PROFILE


@patch('enrolment.helpers.has_company', Mock(return_value=False))
@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
def test_submit_enrolment_handles_api_company_not_found(client):

    with patch('enrolment.helpers.get_company_from_companies_house') as mock:
        mock.side_effect = RequestException(
            response=Mock(status_code=http.client.NOT_FOUND),
            request=Mock(),
        )

        response = client.get(
            reverse('register-submit'),
            {
                'company_number': '12345678',
                'export_status': 'ONE_TWO_YEARS_AGO'
            }
        )

    assert "Company not found" in str(response.content)


@patch('enrolment.helpers.has_company', Mock(return_value=False))
@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
def test_submit_enrolment_handles_api_company_error(client):

    with patch('enrolment.helpers.get_company_from_companies_house') as mock:
        mock.side_effect = RequestException(
            response=Mock(status_code=500),
            request=Mock(),
        )

        response = client.get(
            reverse('register-submit'),
            {
                'company_number': '12345678',
                'export_status': 'ONE_TWO_YEARS_AGO'
            }
        )
    assert 'Error. Please try again later.' in str(response.content)


@patch('enrolment.helpers.has_company', Mock(return_value=False))
@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch('enrolment.helpers.store_companies_house_profile_in_session', Mock())
def test_submit_enrolment_company_number_not_provided(client):
    response = client.get(
        reverse('register-submit'),
        {
            'export_status': 'ONE_TWO_YEARS_AGO'
        }
    )
    assert 'Company number not provided.' in str(response.content)


@patch('enrolment.helpers.has_company', Mock(return_value=False))
@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch('enrolment.helpers.store_companies_house_profile_in_session', Mock())
def test_submit_enrolment_export_status_not_provided(client):
    response = client.get(
        reverse('register-submit'),
        {
            'company_number': '12345678',
        }
    )
    assert 'Export status not provided.' in str(response.content)


@patch('enrolment.helpers.has_company', Mock(return_value=False))
@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch('enrolment.helpers.store_companies_house_profile_in_session', Mock())
@patch('enrolment.helpers.get_company_status_from_session',
       Mock(return_value='not active'))
def test_submit_enrolment_handles_company_not_active(client):

    with patch('enrolment.validators.company_active') as mock:
        mock.side_effect = ValidationError(MESSAGE_COMPANY_NOT_ACTIVE)

        response = client.get(
            reverse('register-submit'),
            {
                'company_number': '12345678',
                'export_status': 'ONE_TWO_YEARS_AGO'
            }
        )

    assert MESSAGE_COMPANY_NOT_ACTIVE in str(response.content)


@patch('enrolment.helpers.has_company', Mock(return_value=False))
@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch('enrolment.helpers.store_companies_house_profile_in_session',
       Mock())
@patch('enrolment.helpers.get_company_status_from_session',
       Mock(return_value='active'))
def test_submit_enrolment_handles_company_already_registered(client):

    with patch('enrolment.validators.company_unique') as mock:
        mock.side_effect = ValidationError('Company already exists')

        response = client.get(
            reverse('register-submit'),
            {
                'company_number': '12345678',
                'export_status': 'ONE_TWO_YEARS_AGO'
            }
        )

    assert 'Company already exists' in str(response.content)


@patch(
    'enrolment.helpers.has_company', Mock(return_value=False)
)
@patch(
    'enrolment.helpers.get_company_number_from_session',
    Mock(return_value='12345678')
)
@patch.object(
    EnrolmentView, 'get_all_cleaned_data', return_value={
        'export_status': 'ONE_TWO_YEARS_AGO'
    }
)
def test_enrolment_form_complete_redirects_to_submit_enrolment(
    sso_request
):
    view = EnrolmentView()
    view.request = sso_request
    response = view.done()

    assert response.status_code == 302
    assert response.url == (
        '/register-submit?company_number=12345678&'
        'export_status=ONE_TWO_YEARS_AGO'
    )
