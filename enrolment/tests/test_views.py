import http
from unittest.mock import patch, Mock

import requests
import pytest

from django.core.urlresolvers import reverse

from enrolment import forms, helpers
from enrolment.views import (
    api_client,
    EnrolmentView,
    EnrolmentInstructionsView,
    EnrolmentSingleStepView,
)
from sso.utils import SSOUser


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


def test_enrolment_instructions_view_handles_no_sso_user(anon_request):
    response = EnrolmentInstructionsView.as_view()(anon_request)

    assert response.template_name == [EnrolmentInstructionsView.template_name]
    assert response.status_code == http.client.OK


@patch('enrolment.helpers.has_company', return_value=True)
def test_enrolment_instructions_view_handles_sso_user_with_company(
    mock_has_company, sso_request, sso_user
):
    response = EnrolmentInstructionsView.as_view()(sso_request)

    mock_has_company.assert_called_once_with(sso_user.id)
    assert response.status_code == http.client.FOUND
    assert response.get('Location') == reverse('company-detail')


@patch.object(helpers, 'has_company', return_value=False)
def test_enrolment_instructions_view_handles_sso_user_without_company(
    mock_has_company, sso_user, sso_request
):
    response = EnrolmentInstructionsView.as_view()(sso_request)

    assert response.template_name == [EnrolmentInstructionsView.template_name]
    assert response.status_code == http.client.OK


@patch('enrolment.helpers.has_company', Mock(return_value=True))
@patch.object(EnrolmentView, 'get_all_cleaned_data', return_value={})
@patch.object(forms, 'serialize_enrolment_forms')
@patch.object(api_client.registration, 'send_form')
def test_enrolment_form_complete_api_client_call(mock_send_form,
                                                 mock_serialize_forms,
                                                 sso_request):
    view = EnrolmentView()
    view.request = sso_request
    mock_serialize_forms.return_value = data = {'field': 'value'}
    view.done()
    mock_send_form.assert_called_once_with(data)


@patch('enrolment.helpers.has_company', Mock(return_value=True))
@patch.object(EnrolmentView, 'serialize_form_data', Mock(return_value={}))
@patch.object(api_client.registration, 'send_form', api_response_200)
def test_enrolment_form_complete_api_client_success(sso_request):
    view = EnrolmentView()
    view.request = sso_request
    response = view.done()
    assert response.template_name == EnrolmentView.success_template


@patch('enrolment.helpers.has_company', Mock(return_value=True))
@patch.object(EnrolmentView, 'serialize_form_data', Mock(return_value={}))
@patch.object(api_client.registration, 'send_form', api_response_400)
def test_enrolment_form_complete_api_client_fail(company_request):
    view = EnrolmentView()
    view.request = company_request
    response = view.done()
    assert response.template_name == EnrolmentView.failure_template


@patch.object(helpers, 'get_company_name_from_session',
              Mock(return_value='Example corp'))
@patch('enrolment.helpers.has_company', Mock(return_value=False))
@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
def test_enrolment_views_use_correct_template(client):
    view_class = EnrolmentView
    for step_name, form in view_class.form_list:
        response = client.get(reverse('register', kwargs={'step': step_name}))

        assert response.template_name == [view_class.templates[step_name]]


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
def test_enrolment_logged_out_has_company_redirects(
    mock_has_company, client
):
    step = EnrolmentView.COMPANY
    url = reverse('register', kwargs={'step': step})
    response = client.get(url)

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == (
         'http://sso.trade.great.dev:8004/accounts/signup/'
         '?next=http%3A//testserver/register/' + step
    )
    mock_has_company.assert_not_called()


def test_companies_house_search_feature_flag_disabled(client, settings):
    settings.NEW_LANDING_PAGE_FEATURE_ENABLED = False

    url = reverse('api-internal-companies-house-search')
    response = client.get(url)

    assert response.status_code == 404


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


@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch('enrolment.helpers.has_company', Mock(return_value=False))
@patch('enrolment.helpers.CompaniesHouseClient.retrieve_profile')
@patch.object(api_client.registration, 'send_form')
def test_enrolment_signle_form_complete_api_client_call(
    mock_send_form, mock_retrieve_profile, client
):
    view_class = EnrolmentSingleStepView
    mock_retrieve_profile.return_value = Mock(
        json=lambda: {
            'company_name': 'Jimbo corp',
            'company_status': 'active',
            'date_of_creation': '01/01/2016'
        }
    )
    url = reverse('register-single-step')
    get_payload = {'company_number': '1234567'}
    post_payload = {
        'company_number': '1234567',
        'export_status': 'YES',
        'terms_agreed': True
    }
    client.get(url, get_payload)
    response = client.post(url, post_payload)

    assert response.status_code == 200
    assert response.template_name == view_class.success_template
    assert mock_send_form.call_count == 1


@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch('enrolment.helpers.has_company', Mock(return_value=False))
@patch('enrolment.helpers.CompaniesHouseClient.retrieve_profile')
@patch.object(api_client.registration, 'send_form')
def test_enrolment_signle_form_api_client_fail(
    mock_send_form, mock_retrieve_profile, client, api_response_400
):
    view_class = EnrolmentSingleStepView
    mock_retrieve_profile.return_value = Mock(
        json=lambda: {
            'company_name': 'Jimbo corp',
            'company_status': 'active',
            'date_of_creation': '01/01/2016'
        }
    )
    mock_send_form.return_value = api_response_400
    url = reverse('register-single-step')
    get_payload = {'company_number': '1234567'}
    post_payload = {
        'company_number': '1234567',
        'export_status': 'YES',
        'terms_agreed': True
    }

    client.get(url, get_payload)
    response = client.post(url, post_payload)
    assert response.template_name == view_class.failure_template


@patch('enrolment.helpers.has_company', return_value=True)
@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
def test_enrolment_single_step_logged_in_has_company_redirects(
    mock_has_company, client, sso_user
):
    url = reverse('register-single-step')
    response = client.get(url)

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == reverse('company-detail')
    mock_has_company.assert_called_once_with(sso_user.id)


@patch('sso.middleware.SSOUserMiddleware.process_request',
       process_request_anon)
def test_landing_page_context_no_sso_user(client):
    response = client.get(reverse('index'))

    assert response.context_data['user_has_company'] is None


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


@patch('enrolment.helpers.has_company', Mock(return_value=True))
@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
def test_landing_page_submit_feature_flag_off(settings, client):
    settings.NEW_LANDING_PAGE_FEATURE_ENABLED = False

    response = client.post(reverse('index'))

    assert response.status_code == 405


@patch('api_client.api_client.company.validate_company_number')
def test_landing_page_submit_invalid_form_shows_errors(
    mock_company_unique, settings, client,
    api_response_validate_company_number_400
):
    mock_company_unique.return_value = api_response_validate_company_number_400
    settings.NEW_LANDING_PAGE_FEATURE_ENABLED = True

    url = reverse('index')
    params = {'company_number': '11111111'}
    response = client.post(url, params)

    assert response.status_code == 200
    assert response.context['form'].errors == {'company_number': ['Not good']}


@patch('enrolment.forms.validators.company_unique')
def test_landing_page_submit_valid_form_redirects(
    mock_company_unique, settings, client
):
    settings.NEW_LANDING_PAGE_FEATURE_ENABLED = True

    url = reverse('index')
    params = {'company_number': '11111111'}
    response = client.post(url, params)

    expected_url = '/register/single/?company_number=11111111'
    assert response.status_code == 302
    assert response.get('Location') == expected_url
