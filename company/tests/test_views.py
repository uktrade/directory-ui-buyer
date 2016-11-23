import http
from unittest.mock import patch, Mock

from directory_validators.constants import choices
import pytest
import requests

from django.core.urlresolvers import reverse

from sso.utils import SSOUser
from company.views import SupplierCaseStudyView
from company import views


default_sector = choices.COMPANY_CLASSIFICATIONS[1][0]


def api_response_200():
    response = requests.Response()
    response.status_code = http.client.OK
    return response


def api_response_400():
    response = requests.Response()
    response.status_code = http.client.BAD_REQUEST
    return response


def process_request(self, request):
    request.sso_user = sso_user()


@pytest.fixture(scope='session')
def image_one(tmpdir_factory):
    return tmpdir_factory.mktemp('media').join('image_one.png').write('1')


@pytest.fixture(scope='session')
def image_two(tmpdir_factory):
    return tmpdir_factory.mktemp('media').join('image_two.png').write('2')


@pytest.fixture(scope='session')
def image_three(tmpdir_factory):
    return tmpdir_factory.mktemp('media').join('image_three.png').write('3')


@pytest.fixture(scope='session')
def video(tmpdir_factory):
    return tmpdir_factory.mktemp('media').join('video.wav').write('video')


@pytest.fixture
def all_case_study_data(video, image_three, image_two, image_one):
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
        'video_one': video,
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
def supplier_case_study_rich_data(video, image_three, image_two, image_one):
    step = SupplierCaseStudyView.RICH_MEDIA
    return {
        'supplier_case_study_view-current_step': step,
        SupplierCaseStudyView.RICH_MEDIA + '-image_one': image_one,
        SupplierCaseStudyView.RICH_MEDIA + '-image_two': image_two,
        SupplierCaseStudyView.RICH_MEDIA + '-image_three': image_three,
        SupplierCaseStudyView.RICH_MEDIA + '-video_one': video,
        SupplierCaseStudyView.RICH_MEDIA + '-testimonial': 'Great',
    }


@pytest.fixture
def sso_user():
    return SSOUser(
        id=1,
        email='jim@example.com',
    )


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
@patch('enrolment.helpers.user_has_verified_company', Mock(return_value=True))
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
@patch('enrolment.helpers.user_has_verified_company', Mock(return_value=True))
@patch.object(views.api_client.company, 'create_supplier_case_study')
def test_case_study_create_api_failure(
    mock_create_case_study, supplier_case_study_end_to_end
):
    mock_create_case_study.return_value = api_response_400()

    response = supplier_case_study_end_to_end()

    assert response.status_code == http.client.OK
    assert response.template_name == SupplierCaseStudyView.failure_template


@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch('enrolment.helpers.user_has_verified_company', Mock(return_value=True))
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
@patch('enrolment.helpers.user_has_verified_company', Mock(return_value=True))
@patch.object(views.api_client.company, 'update_supplier_case_study')
def test_case_study_update_api_failure(
    mock_update_case_study, supplier_case_study_end_to_end
):
    mock_update_case_study.return_value = api_response_400()

    response = supplier_case_study_end_to_end(case_study_id='1')

    assert response.status_code == http.client.OK
    assert response.template_name == SupplierCaseStudyView.failure_template
