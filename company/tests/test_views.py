import http
from unittest.mock import patch, Mock

from directory_validators.constants import choices
import pytest
import requests

from django.core.urlresolvers import reverse

from sso.utils import SSOUser
from company.views import SupplierCaseStudyView
from company import helpers, views


default_sector = choices.COMPANY_CLASSIFICATIONS[1][0]


def api_response_200():
    response = requests.Response()
    response.status_code = http.client.OK
    return response


def api_response_400():
    response = requests.Response()
    response.status_code = http.client.BAD_REQUEST
    return response


def api_response_404():
    response = requests.Response()
    response.status_code = http.client.NOT_FOUND
    return response


def retrieve_supplier_case_study_200():
    response = api_response_200()
    response.json = lambda: {'field': 'value'}
    return response


def process_request(self, request):
    request.sso_user = sso_user()


@pytest.fixture
def sso_user():
    return SSOUser(
        id=1,
        email='jim@example.com',
    )


@pytest.fixture
def sso_request(rf, client, sso_user):
    request = rf.get('/')
    request.sso_user = sso_user
    request.session = client.session
    return request


@pytest.fixture(scope='session')
def image_one(tmpdir_factory):
    return tmpdir_factory.mktemp('media').join('image_one.png').write('1')


@pytest.fixture(scope='session')
def image_two(tmpdir_factory):
    return tmpdir_factory.mktemp('media').join('image_two.png').write('2')


@pytest.fixture(scope='session')
def image_three(tmpdir_factory):
    return tmpdir_factory.mktemp('media').join('image_three.png').write('3')


@pytest.fixture
def all_case_study_data(image_three, image_two, image_one):
    return {
        'title': 'Example',
        'description': 'Great',
        'sector': default_sector,
        'website': 'http://www.example.com',
        'year': '2000',
        'keywords': 'good, great',
        'testimonial': 'Great',
        'image_one': image_one,
        'image_two': image_two,
        'image_three': image_three,
    }


@pytest.fixture
def supplier_case_study_basic_data():
    return {
        'supplier_case_study_view-current_step': SupplierCaseStudyView.BASIC,
        SupplierCaseStudyView.BASIC + '-title': 'Example',
        SupplierCaseStudyView.BASIC + '-description': 'Great',
        SupplierCaseStudyView.BASIC + '-sector': default_sector,
        SupplierCaseStudyView.BASIC + '-website': 'http://www.example.com',
        SupplierCaseStudyView.BASIC + '-year': '2000',
        SupplierCaseStudyView.BASIC + '-keywords': 'good, great'
    }


@pytest.fixture
def supplier_case_study_rich_data(image_three, image_two, image_one):
    step = SupplierCaseStudyView.RICH_MEDIA
    return {
        'supplier_case_study_view-current_step': step,
        SupplierCaseStudyView.RICH_MEDIA + '-image_one': image_one,
        SupplierCaseStudyView.RICH_MEDIA + '-image_two': image_two,
        SupplierCaseStudyView.RICH_MEDIA + '-image_three': image_three,
        SupplierCaseStudyView.RICH_MEDIA + '-testimonial': 'Great',
    }


@pytest.fixture
def supplier_case_study_end_to_end(
    client, supplier_case_study_basic_data, supplier_case_study_rich_data
):
    # loop over each step in the supplier case study wizard and post valid data
    data_step_pairs = [
        [SupplierCaseStudyView.BASIC, supplier_case_study_basic_data],
        [SupplierCaseStudyView.RICH_MEDIA, supplier_case_study_rich_data],
    ]

    def inner(case_study_id=''):
        url = reverse('company-case-study-edit', kwargs={'id': case_study_id})
        for key, data in data_step_pairs:
            response = client.post(url, data)
        return response
    return inner


@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch('enrolment.helpers.has_verified_company', Mock(return_value=True))
@patch('api_client.api_client.company.retrieve_supplier_case_study')
def test_case_study_edit_retrieves_data(
    mock_retrieve_supplier_case_study, client
):
    url = reverse('company-case-study-edit', kwargs={'id': '2'})
    client.get(url)

    mock_retrieve_supplier_case_study.assert_called_once_with(
        case_study_id='2', sso_user_id=1,
    )


@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch('enrolment.helpers.has_verified_company', Mock(return_value=True))
@patch('api_client.api_client.company.retrieve_supplier_case_study')
def test_case_study_edit_exposes_api_response_data(
    mock_retrieve_case_study, client
):
    mock_retrieve_case_study.return_value = retrieve_supplier_case_study_200()

    url = reverse('company-case-study-edit', kwargs={'id': '2'})
    response = client.get(url)

    assert response.context['form'].initial == {'field': 'value'}


@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch('enrolment.helpers.has_verified_company', Mock(return_value=True))
@patch('api_client.api_client.company.retrieve_supplier_case_study')
def test_case_study_edit_handles_api_error(
    mock_retrieve_case_study, client
):
    mock_retrieve_case_study.return_value = api_response_400()

    url = reverse('company-case-study-edit', kwargs={'id': '2'})
    with pytest.raises(requests.exceptions.HTTPError):
        client.get(url)


@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch('enrolment.helpers.has_verified_company', Mock(return_value=True))
@patch.object(views.api_client.company, 'create_supplier_case_study')
def test_case_study_create_api_success(
    mock_create_case_study, supplier_case_study_end_to_end, sso_user,
    all_case_study_data
):
    mock_create_case_study.return_value = api_response_200()

    response = supplier_case_study_end_to_end()

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == reverse('company-detail')
    mock_create_case_study.assert_called_once_with(
        data=all_case_study_data,
        sso_user_id=sso_user.id,
    )


@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch('enrolment.helpers.has_verified_company', Mock(return_value=True))
@patch.object(views.api_client.company, 'create_supplier_case_study')
def test_case_study_create_api_failure(
    mock_create_case_study, supplier_case_study_end_to_end
):
    mock_create_case_study.return_value = api_response_400()

    response = supplier_case_study_end_to_end()

    assert response.status_code == http.client.OK
    assert response.template_name == SupplierCaseStudyView.failure_template


@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch('enrolment.helpers.has_verified_company', Mock(return_value=True))
@patch.object(views.api_client.company, 'update_supplier_case_study')
def test_case_study_update_api_success(
    mock_update_case_study, supplier_case_study_end_to_end, sso_user,
    all_case_study_data,
):
    mock_update_case_study.return_value = api_response_200()

    response = supplier_case_study_end_to_end(case_study_id='1')

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == reverse('company-detail')
    mock_update_case_study.assert_called_once_with(
        data=all_case_study_data,
        case_study_id='1',
        sso_user_id=sso_user.id,
    )


@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch('enrolment.helpers.has_verified_company', Mock(return_value=True))
@patch.object(views.api_client.company, 'update_supplier_case_study')
def test_case_study_update_api_failure(
    mock_update_case_study, supplier_case_study_end_to_end
):
    mock_update_case_study.return_value = api_response_400()

    response = supplier_case_study_end_to_end(case_study_id='1')

    assert response.status_code == http.client.OK
    assert response.template_name == SupplierCaseStudyView.failure_template


@patch('enrolment.helpers.has_verified_company', Mock(return_value=True))
@patch.object(views.api_client.company, 'retrieve_profile', Mock)
@patch.object(helpers, 'get_company_profile_from_response')
def test_company_profile_details_exposes_context(
    mock_get_company_profile_from_response, sso_request
):
    mock_get_company_profile_from_response.return_value = {}
    view = views.SupplierCompanyProfileDetailView.as_view()
    response = view(sso_request)
    assert response.status_code == http.client.OK
    assert response.template_name == [
        views.SupplierCompanyProfileDetailView.template_name
    ]

    assert response.context_data['company'] == {}
    assert response.context_data['show_edit_links'] is True


@patch('enrolment.helpers.has_verified_company', Mock(return_value=True))
@patch.object(helpers, 'get_company_profile_from_response')
@patch.object(views.api_client.company, 'retrieve_profile')
def test_company_profile_details_calls_api(
    mock_retrieve_profile, mock_get_company_profile_from_response,
    sso_request
):
    mock_get_company_profile_from_response.return_value = {}
    view = views.SupplierCompanyProfileDetailView.as_view()

    view(sso_request)

    assert mock_retrieve_profile.called_once_with(1)


@patch('enrolment.helpers.has_verified_company', Mock(return_value=True))
@patch.object(helpers, 'get_company_profile_from_response')
@patch.object(views.api_client.company, 'retrieve_profile')
def test_company_profile_details_handles_bad_status(
    mock_retrieve_profile, mock_get_company_profile_from_response,
    sso_request
):
    mock_retrieve_profile.return_value = api_response_400()
    mock_get_company_profile_from_response.return_value = {}
    view = views.SupplierCompanyProfileDetailView.as_view()

    with pytest.raises(requests.exceptions.HTTPError):
        view(sso_request)


@patch('enrolment.helpers.has_verified_company', Mock(return_value=True))
@patch.object(views.api_client.company,
              'retrieve_public_profile_by_companies_house_number', Mock)
@patch.object(helpers, 'get_public_company_profile_from_response')
def test_public_company_profile_details_exposes_context(
    mock_get_public_company_profile_from_response, client
):
    mock_get_public_company_profile_from_response.return_value = {}
    url = reverse(
        'public-company-profiles-detail', kwargs={'company_number': '01234567'}
    )
    response = client.get(url)
    assert response.status_code == http.client.OK
    assert response.template_name == [
        views.PublicProfileDetailView.template_name
    ]
    assert response.context_data['company'] == {}
    assert response.context_data['show_edit_links'] is False


@patch('enrolment.helpers.has_verified_company', Mock(return_value=True))
@patch.object(helpers, 'get_public_company_profile_from_response')
@patch.object(views.api_client.company,
              'retrieve_public_profile_by_companies_house_number')
def test_public_company_profile_details_calls_api(
    mock_retrieve_public_profile,
    mock_get_public_company_profile_from_response, client
):
    mock_get_public_company_profile_from_response.return_value = {}
    url = reverse(
        'public-company-profiles-detail', kwargs={'company_number': '01234567'}
    )
    client.get(url)

    assert mock_retrieve_public_profile.called_once_with(1)


@patch('enrolment.helpers.has_verified_company', Mock(return_value=True))
@patch.object(helpers, 'get_public_company_profile_from_response')
@patch.object(views.api_client.company,
              'retrieve_public_profile_by_companies_house_number')
def test_public_company_profile_details_handles_bad_status(
    mock_retrieve_public_profile,
    mock_get_public_company_profile_from_response, client
):
    mock_retrieve_public_profile.return_value = api_response_400()
    url = reverse(
        'public-company-profiles-detail', kwargs={'company_number': '01234567'}
    )

    with pytest.raises(requests.exceptions.HTTPError):
        client.get(url)


@patch('enrolment.helpers.has_verified_company', Mock(return_value=True))
def test_company_profile_list_exposes_context(
    client, api_response_list_public_profile_200
):
    url = reverse('public-company-profiles-list')
    params = {'sectors': choices.COMPANY_CLASSIFICATIONS[1][0]}
    expected_companies = helpers.get_company_list_from_response(
        api_response_list_public_profile_200
    )['results']

    response = client.get(url, params)

    assert response.status_code == http.client.OK
    assert response.template_name == views.PublicProfileListView.template_name
    assert response.context_data['companies'] == expected_companies
    assert response.context_data['pagination'].paginator.count == 20


@patch('enrolment.helpers.has_verified_company', Mock(return_value=True))
def test_company_profile_list_exposes_selected_sector_label(client):
    url = reverse('public-company-profiles-list')
    params = {'sectors': choices.COMPANY_CLASSIFICATIONS[1][0]}
    response = client.get(url, params)

    expected_label = choices.COMPANY_CLASSIFICATIONS[1][1]
    assert response.context_data['selected_sector_label'] == expected_label


@patch('enrolment.helpers.has_verified_company', Mock(return_value=True))
@patch.object(views.api_client.company, 'list_public_profiles')
def test_company_profile_list_calls_api(
    mock_list_public_profiles, client
):
    url = reverse('public-company-profiles-list')
    params = {'sectors': choices.COMPANY_CLASSIFICATIONS[1][0]}
    client.get(url, params)

    assert mock_list_public_profiles.called_once_with(
        sectors=choices.COMPANY_CLASSIFICATIONS[1][0],
    )


@patch('enrolment.helpers.has_verified_company', Mock(return_value=True))
@patch.object(views.api_client.company, 'list_public_profiles')
def test_company_profile_list_handles_bad_status(
    mock_retrieve_public_profile, client
):
    mock_retrieve_public_profile.return_value = api_response_400()
    url = reverse('public-company-profiles-list')
    params = {'sectors': choices.COMPANY_CLASSIFICATIONS[1][0]}
    with pytest.raises(requests.exceptions.HTTPError):
        client.get(url, params)


@patch('enrolment.helpers.has_verified_company', Mock(return_value=True))
def test_company_profile_list_handles_no_form_data(client):
    url = reverse('public-company-profiles-list')
    response = client.get(url, {})

    assert response.context_data['form'].errors == {}


@patch('enrolment.helpers.has_verified_company', Mock(return_value=True))
@patch.object(views.api_client.company, 'list_public_profiles')
def test_company_profile_list_handles_empty_page(mock_list_profiles, client):
    mock_list_profiles.return_value = api_response_404()
    url = reverse('public-company-profiles-list')
    response = client.get(url, {'sectors': 'WATER', 'page': 10})

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == '{url}?sectors=WATER'.format(url=url)
