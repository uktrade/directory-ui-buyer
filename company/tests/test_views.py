import http
from http.cookies import SimpleCookie
from unittest.mock import call, patch, Mock, ANY
import urllib

from directory_constants.constants import choices
from directory_api_client.client import api_client
import pytest
import requests

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView

from sso.utils import SSOUser
from company import forms, helpers, state_requirements, views, validators
from company.tests.helpers import create_test_image


default_sector = choices.INDUSTRIES[1][0]


patch_check_company_owner_redirect = patch(
    'company.state_requirements.IsCompanyOwner.is_user_in_required_state',
    Mock(return_value=True)
)
patch_check_company_unverified_redirect = patch(
    (
        'company.state_requirements.HasUnverifiedCompany.'
        'is_user_in_required_state'
    ),
    Mock(return_value=True)
)
patch_check_not_company_owner_redirect = patch(
    'company.state_requirements.NotCompanyOwner.is_user_in_required_state',
    Mock(return_value=True)
)
patch_check_no_company_redirect = patch(
    'company.state_requirements.NoCompany.is_user_in_required_state',
    Mock(return_value=True)
)


def create_response(status_code, json_body={}):
    response = requests.Response()
    response.status_code = status_code
    response.json = lambda: json_body
    return response


@pytest.fixture
def api_response_get_invite_200():
    return create_response(
        status_code=http.client.OK, json_body={'company_name': 'A Company'}
    )


@pytest.fixture
def api_response_collaborators_200():
    return create_response(
        status_code=http.client.OK, json_body=[
            {'sso_id': 1, 'company_email': 'test@example.com'},
        ]
    )


@pytest.fixture
def logged_in_client(client, sso_user):
    def process_request(self, request):
        request.sso_user = sso_user

    stub = patch(
        'sso.middleware.SSOUserMiddleware.process_request', process_request
    )
    stub.start()
    yield client
    stub.stop()


@pytest.fixture
def has_company_client(logged_in_client, retrieve_profile_data):
    response = create_response(
        status_code=http.client.OK,
        json_body={**retrieve_profile_data, 'is_verified': True}
    )
    stub = patch.object(
        api_client.company, 'retrieve_private_profile',
        Mock(return_value=response)
    )
    stub.start()
    yield logged_in_client
    stub.stop()


@pytest.fixture
def company_request(rf, client, sso_user):
    request = rf.get('/')
    request.sso_user = sso_user
    request.session = client.session
    return request


@pytest.fixture
def sso_user():
    return SSOUser(
        id=1,
        email='jim@example.com',
        session_id='213'
    )


@pytest.fixture
def sso_request(rf, client, sso_user):
    request = rf.get('/')
    request.sso_user = sso_user
    request.session = client.session
    return request


@pytest.fixture()
def image_one():
    return UploadedFile(
        file=create_test_image('png'),
        name='one.png',
        content_type='image/png',
        size=100,
    )


@pytest.fixture()
def image_two():
    return UploadedFile(
        file=create_test_image('png'),
        name='one.png',
        content_type='image/png',
        size=100,
    )


@pytest.fixture()
def image_three():
    return UploadedFile(
        file=create_test_image('png'),
        name='one.png',
        content_type='image/png',
        size=100,
    )


@pytest.fixture()
def all_case_study_data(image_three, image_two, image_one):
    return {
        'title': 'Example',
        'description': 'Great',
        'short_summary': 'Nice',
        'sector': default_sector,
        'website': 'http://www.example.com',
        'keywords': 'good, great',
        'testimonial': 'Great',
        'testimonial_name': 'Neville',
        'testimonial_job_title': 'Abstract hat maker',
        'testimonial_company': 'Imaginary hats Ltd',
        'image_one': image_one,
        'image_two': image_two,
        'image_three': image_three,
        'image_one_caption': 'nice image',
        'image_two_caption': '',
        'image_three_caption': '',

    }


@pytest.fixture
def supplier_case_study_basic_data(all_case_study_data):
    view = views.SupplierCaseStudyWizardView
    return {
        'supplier_case_study_wizard_view-current_step': view.BASIC,
        view.BASIC + '-title': all_case_study_data['title'],
        view.BASIC + '-short_summary': all_case_study_data['short_summary'],
        view.BASIC + '-description': all_case_study_data['description'],
        view.BASIC + '-sector': all_case_study_data['sector'],
        view.BASIC + '-website': all_case_study_data['website'],
        view.BASIC + '-keywords': all_case_study_data['keywords'],
    }


@pytest.fixture
def supplier_case_study_rich_data(all_case_study_data):
    step = views.SupplierCaseStudyWizardView.RICH_MEDIA
    data = all_case_study_data
    return {
        'supplier_case_study_wizard_view-current_step': step,
        step + '-image_one': data['image_one'],
        step + '-image_one_caption': data['image_one_caption'],
        step + '-image_two': data['image_two'],
        step + '-image_three': data['image_three'],
        step + '-testimonial': data['description'],
        step + '-testimonial_name': data['testimonial_name'],
        step + '-testimonial_job_title': data['testimonial_job_title'],
        step + '-testimonial_company': data['testimonial_company'],
    }


@pytest.fixture
def all_company_profile_data():
    return {
        'name': 'Example Corp.',
        'website': 'http://www.example.com',
        'keywords': 'Nice, Great',
        'employees': choices.EMPLOYEES[1][0],
        'sectors': [choices.INDUSTRIES[3][0]],
        'postal_full_name': 'Jeremy',
        'address_line_1': '123 Fake Street',
        'address_line_2': 'Fakeville',
        'locality': 'London',
        'postal_code': 'E14 6XK',
        'po_box': 'abc',
        'country': 'GB',
        'export_destinations': ['CN', 'IN'],
        'export_destinations_other': 'West Philadelphia',
        'has_exported_before': True,
    }


@pytest.fixture
def all_social_links_data():
    return {
        'twitter_url': 'http://www.twitter.com',
        'facebook_url': 'http://www.facebook.com',
        'linkedin_url': 'http://www.linkedin.com',
    }


@pytest.fixture
def company_profile_social_links_data(all_social_links_data):
    view = views.CompanySocialLinksEditView
    return {
        'company_social_links_edit_view-current_step': view.SOCIAL,
        view.SOCIAL + '-twitter_url': all_social_links_data['twitter_url'],
        view.SOCIAL + '-linkedin_url': all_social_links_data['linkedin_url'],
        view.SOCIAL + '-facebook_url': all_social_links_data['facebook_url'],
    }


@pytest.fixture
def company_profile_address_data(all_company_profile_data):
    view = views.SupplierAddressEditView
    data = all_company_profile_data
    return {
        'company_profile_edit_view-current_step': view.ADDRESS,
        view.ADDRESS + '-postal_full_name': data['postal_full_name'],
        view.ADDRESS + '-address_line_1': data['address_line_1'],
        view.ADDRESS + '-address_line_2': data['address_line_2'],
        view.ADDRESS + '-locality': data['locality'],
        view.ADDRESS + '-postal_code': data['postal_code'],
        view.ADDRESS + '-po_box': data['po_box'],
        view.ADDRESS + '-country': data['country'],
        view.ADDRESS + '-address_confirmed': True,
        view.ADDRESS + '-signature': None,
    }


@pytest.fixture
def supplier_address_data_standalone(company_profile_address_data):
    step = views.SupplierAddressEditView.ADDRESS
    data = company_profile_address_data
    data['supplier_address_edit_view-current_step'] = step
    return data


@pytest.fixture
def company_profile_basic_data(all_company_profile_data):
    view = views.CompanyProfileEditView
    data = all_company_profile_data
    return {
        'company_profile_edit_view-current_step': view.BASIC,
        view.BASIC + '-name': data['name'],
        view.BASIC + '-website': data['website'],
        view.BASIC + '-keywords': data['keywords'],
        view.BASIC + '-employees': data['employees'],
    }


@pytest.fixture
def company_profile_key_facts_standalone_data(company_profile_basic_data):
    data = company_profile_basic_data
    step = views.SupplierBasicInfoEditView.BASIC
    data['supplier_basic_info_edit_view-current_step'] = step
    return data


@pytest.fixture
def company_profile_classification_data(all_company_profile_data):
    view = views.CompanyProfileEditView
    data = all_company_profile_data
    step = view.CLASSIFICATION
    return {
        'company_profile_edit_view-current_step': step,
        step + '-sectors': data['sectors'],
        step + '-export_destinations': data['export_destinations'],
        step + '-export_destinations_other': data['export_destinations_other'],
        step + '-has_exported_before': data['has_exported_before'],
    }


@pytest.fixture
def company_profile_sectors_standalone_data(
    company_profile_classification_data
):
    data = company_profile_classification_data
    step = views.SupplierClassificationEditView.CLASSIFICATION
    data['supplier_classification_edit_view-current_step'] = step
    return data


@pytest.fixture
def company_profile_contact_standalone_data():
    step = views.SupplierContactEditView.CONTACT
    return {
        'supplier_contact_edit_view-current_step': step,
        step + '-email_address': 'test@example.com',
        step + '-email_full_name': 'test',
        step + '-website': 'http://www.example.com',
    }


@pytest.fixture
def all_address_verification_data():
    return {
        'code': 'x'*12
    }


@pytest.fixture
def address_verification_address_data(all_address_verification_data):
    view = views.CompanyAddressVerificationView
    data = all_address_verification_data
    step = view.ADDRESS
    return {
        'company_address_verification_view-current_step': step,
        step + '-code': data['code'],
    }


@pytest.fixture
def supplier_case_study_end_to_end(
    has_company_client, supplier_case_study_basic_data,
    supplier_case_study_rich_data
):
    # loop over each step in the supplier case study wizard and post valid data
    view = views.SupplierCaseStudyWizardView
    data_step_pairs = [
        [view.BASIC, supplier_case_study_basic_data],
        [view.RICH_MEDIA, supplier_case_study_rich_data],
    ]

    def inner(case_study_id=None):
        if case_study_id:
            url = reverse(
                'company-case-study-edit', kwargs={'id': case_study_id}
            )
        else:
            url = reverse('company-case-study-create')
        for key, data in data_step_pairs:
            response = has_company_client.post(url, data)
        return response
    return inner


@pytest.fixture
def address_verification_end_to_end(
    has_company_client, address_verification_address_data
):
    view = views.CompanyAddressVerificationView
    data_step_pairs = [
        [view.ADDRESS, address_verification_address_data],
    ]

    def inner(case_study_id=''):
        url = reverse('verify-company-address-confirm')
        for key, data in data_step_pairs:
            response = has_company_client.post(url, data)
        return response
    return inner


@pytest.fixture
def send_verification_letter_end_to_end(
    has_company_client, all_company_profile_data
):
    all_data = all_company_profile_data
    view = views.SendVerificationLetterView
    address_data = {
        'company_profile_edit_view-current_step': view.ADDRESS,
        view.ADDRESS + '-postal_full_name': all_data['postal_full_name'],
        view.ADDRESS + '-address_confirmed': True,
    }

    data_step_pairs = [
        [view.ADDRESS, address_data],
    ]

    def inner():
        url = reverse('verify-company-address')
        for key, data in data_step_pairs:
            data['send_verification_letter_view-current_step'] = key
            response = has_company_client.post(url, data)
        return response
    return inner


@pytest.fixture
def company_profile_edit_end_to_end(
    has_company_client, company_profile_basic_data,
    company_profile_classification_data
):
    # loop over each step in the supplier case study wizard and post valid data
    view = views.CompanyProfileEditView
    data_step_pairs = [
        [view.BASIC, company_profile_basic_data],
        [view.CLASSIFICATION, company_profile_classification_data],
    ]

    def inner():
        url = reverse('company-edit')
        for key, data in data_step_pairs:
            response = has_company_client.post(url, data)
        return response
    return inner


@pytest.fixture
def company_profile_edit_goto_step(
    has_company_client, company_profile_basic_data,
    company_profile_classification_data,
):
    # loop over each step in the supplier case study wizard and post valid data
    view = views.CompanyProfileEditView
    data_step_pairs = [
        [view.BASIC, company_profile_basic_data],
        [view.CLASSIFICATION, company_profile_classification_data],
    ]

    def inner(step):
        index = next(
            data_step_pairs.index(item)
            for item in data_step_pairs
            if item[0] == step
        )
        url = reverse('company-edit')
        if index == 0:
            response = has_company_client.get(url)
        else:
            for key, data in data_step_pairs[:index]:
                response = has_company_client.post(url, data, follow=True)
        return response
    return inner


@patch.object(api_client.company, 'retrieve_private_case_study')
def test_case_study_edit_retrieves_data(
    mock_retrieve_supplier_case_study, has_company_client
):
    url = reverse('company-case-study-edit', kwargs={'id': '2'})
    has_company_client.get(url)

    mock_retrieve_supplier_case_study.assert_called_once_with(
        case_study_id='2', sso_session_id='213',
    )


@patch.object(
    api_client.company, 'retrieve_private_case_study',
    Mock(return_value=create_response(200, {'field': 'value'}))
)
def test_case_study_edit_exposes_api_response_data(has_company_client):
    url = reverse('company-case-study-edit', kwargs={'id': '2'})
    response = has_company_client.get(url)

    assert response.context['form'].initial == {'field': 'value'}


@patch.object(api_client.company, 'retrieve_private_case_study')
def test_case_study_edit_handles_api_error(
    mock_retrieve_case_study, has_company_client
):
    mock_retrieve_case_study.return_value = create_response(400)

    url = reverse('company-case-study-edit', kwargs={'id': '2'})
    with pytest.raises(requests.exceptions.HTTPError):
        has_company_client.get(url)


@patch.object(
    api_client.company, 'create_case_study', return_value=create_response(201)
)
def test_case_study_create_api_success(
    mock_create_case_study, supplier_case_study_end_to_end, sso_user,
    all_case_study_data
):
    response = supplier_case_study_end_to_end()
    assert response.status_code == http.client.FOUND
    assert response.url == reverse('company-detail')
    data = {
        **all_case_study_data,
        'image_one': ANY, 'image_two': ANY, 'image_three': ANY,
    }
    # django converts uploaded files to UploadedFile, which makes
    # `assert_called_once_with` tricky.

    assert mock_create_case_study.call_count == 1
    assert mock_create_case_study.call_args == call(
        data=data,
        sso_session_id=sso_user.session_id,
    )


@patch.object(api_client.company, 'create_case_study')
def test_case_study_create_api_failure(
    mock_create_case_study, supplier_case_study_end_to_end
):
    mock_create_case_study.return_value = create_response(400)

    with pytest.raises(requests.exceptions.HTTPError):
        supplier_case_study_end_to_end()


@patch.object(
    api_client.company, 'update_case_study', return_value=create_response(201)
)
def test_case_study_update_api_success(
    mock_update_case_study, supplier_case_study_end_to_end, sso_user,
    all_case_study_data
):
    response = supplier_case_study_end_to_end(case_study_id='1')

    assert response.status_code == http.client.FOUND
    assert response.url == reverse('company-detail')
    # django converts uploaded files to UploadedFile, which makes
    # `assert_called_once_with` tricky.
    data = {
        **all_case_study_data,
        'image_one': ANY, 'image_two': ANY, 'image_three': ANY,
    }
    mock_update_case_study.assert_called_once_with(
        data=data,
        case_study_id='1',
        sso_session_id=sso_user.session_id,
    )


@patch.object(api_client.company, 'retrieve_private_case_study')
def test_case_study_get_api_not_found(
    mock_retrieve_private_case_study, has_company_client
):
    mock_retrieve_private_case_study.return_value = create_response(404)
    url = reverse('company-case-study-edit', kwargs={'id': 1221})

    response = has_company_client.get(url)

    assert response.status_code == http.client.NOT_FOUND


@patch.object(api_client.company, 'update_case_study')
def test_case_study_update_api_failure(
    mock_update_case_study, supplier_case_study_end_to_end
):
    mock_update_case_study.return_value = create_response(400)

    with pytest.raises(requests.exceptions.HTTPError):
        supplier_case_study_end_to_end(case_study_id='1')


@patch.object(helpers, 'get_company_profile')
@patch.object(forms, 'is_optional_profile_values_set', return_value=True)
def test_company_profile_details_exposes_context(
    mock_is_optional_profile_values_set, mock_get_company_profile,
    retrieve_profile_data, has_company_client
):
    company = retrieve_profile_data
    mock_get_company_profile.return_value = company

    response = has_company_client.get(reverse('company-detail'))

    assert response.status_code == http.client.OK
    assert response.template_name == [
        views.CompanyProfileDetailView.template_name
    ]

    assert response.context_data['company'] == helpers.format_company_details(
        company
    )
    assert company['sectors'] == ['SECURITY']
    assert response.context_data['show_wizard_links'] is False
    mock_is_optional_profile_values_set.assert_called_once_with(company)


@patch.object(helpers, 'get_company_profile')
@patch.object(api_client.company, 'retrieve_private_profile')
def test_company_profile_details_calls_api(
    mock_retrieve_profile, mock_get_company_profile, sso_request,
    retrieve_profile_data
):
    mock_get_company_profile.return_value = retrieve_profile_data
    view = views.CompanyProfileDetailView.as_view()

    view(sso_request)

    assert mock_retrieve_profile.called_once_with(1)


@patch.object(helpers, 'get_company_profile_from_response')
@patch.object(api_client.company, 'retrieve_private_profile')
def test_company_profile_details_handles_bad_status(
    mock_retrieve_profile, mock_get_company_profile_from_response,
    sso_request
):
    mock_retrieve_profile.return_value = create_response(400)
    mock_get_company_profile_from_response.return_value = {}
    view = views.CompanyProfileDetailView.as_view()

    with pytest.raises(requests.exceptions.HTTPError):
        view(sso_request)


@patch.object(views.CompanyDescriptionEditView, 'serialize_form_data',
              Mock(return_value={'field': 'value'}))
@patch.object(api_client.company, 'update_profile')
def test_company_profile_description_api_client_call(mock_update_profile,
                                                     company_request):

    view = views.CompanyDescriptionEditView()
    view.request = company_request
    view.done()
    mock_update_profile.assert_called_once_with(
        sso_session_id='213', data={'field': 'value'}
    )


@patch(
    'company.views.CompanyDescriptionEditView.serialize_form_data',
    Mock(return_value={})
)
@patch.object(
    api_client.company, 'update_profile',
    Mock(return_value=create_response(200))
)
def test_company_profile_description_api_client_success(company_request):
    view = views.CompanyDescriptionEditView()
    view.request = company_request
    response = view.done()
    assert response.status_code == http.client.FOUND


@patch.object(views.CompanyDescriptionEditView, 'serialize_form_data',
              Mock(return_value={}))
@patch.object(api_client.company, 'update_profile')
def test_company_profile_description_api_client_failure(
    mock_update_profile, company_request
):
    mock_update_profile.return_value = create_response(400)

    view = views.CompanyDescriptionEditView()
    view.request = company_request

    with pytest.raises(requests.exceptions.HTTPError):
        view.done()


@patch.object(api_client.company, 'retrieve_private_profile')
def test_company_description_edit_calls_api(
    mock_retrieve_profile, company_request, api_response_company_profile_200
):
    mock_retrieve_profile.return_value = api_response_company_profile_200
    view = views.CompanyDescriptionEditView.as_view()

    view(company_request)

    assert mock_retrieve_profile.called_once_with(1)


@patch.object(api_client.company, 'retrieve_private_profile')
def test_company_profile_description_exposes_api_result_to_form(
    mock_retrieve_profile, company_request, api_response_company_profile_200
):
    mock_retrieve_profile.return_value = api_response_company_profile_200
    view = views.CompanyDescriptionEditView.as_view()
    expected = api_response_company_profile_200.json()

    response = view(company_request)

    assert response.context_data['form'].initial == {
        **expected,
        'sectors': expected['sectors'][0],
    }


@patch.object(api_client.company, 'retrieve_private_profile')
def test_company_description_edit_handles_bad_api_response(
    mock_retrieve_profile, company_request
):

    mock_retrieve_profile.return_value = create_response(400)
    view = views.CompanyDescriptionEditView.as_view()

    with pytest.raises(requests.exceptions.HTTPError):
        view(company_request)


def test_company_description_edit_views_use_correct_template(
        client, rf, sso_user):
    request = rf.get(reverse('company-edit-description'))
    request.sso_user = sso_user
    request.session = client.session
    view_class = views.CompanyDescriptionEditView
    assert view_class.form_list
    for form_pair in view_class.form_list:
        step_name = form_pair[0]
        view = view_class.as_view(form_list=(form_pair,))
        response = view(request)

        assert response.template_name == [view_class.templates[step_name]]


@patch.object(views.CompanyProfileEditView, 'serialize_form_data',
              Mock(return_value={'field': 'value'}))
@patch.object(api_client.company, 'update_profile')
def test_company_profile_edit_api_client_call(
    mock_update_profile, company_request, retrieve_profile_data
):
    view = views.CompanyProfileEditView()
    view.company_profile = retrieve_profile_data
    view.request = company_request
    view.done()
    mock_update_profile.assert_called_once_with(
        sso_session_id='213', data={'field': 'value'}
    )


@patch.object(
    views.CompanyProfileEditView, 'serialize_form_data', Mock(return_value={})
)
@patch.object(
    api_client.company, 'update_profile',
    Mock(return_value=create_response(200))
)
def test_company_profile_edit_api_client_success(
    company_request, retrieve_profile_data, settings
):
    view = views.CompanyProfileEditView()
    view.request = company_request
    view.company_profile = retrieve_profile_data
    response = view.done()
    assert response.status_code == 302
    assert response.url == reverse('company-detail')


@patch.object(views.CompanyProfileEditView, 'serialize_form_data',
              Mock(return_value={}))
@patch.object(api_client.company, 'update_profile')
def test_company_profile_edit_api_client_failure(
    mock_update_profile, company_request, retrieve_profile_data
):
    mock_update_profile.return_value = create_response(400)

    view = views.CompanyProfileEditView()
    view.company_profile = retrieve_profile_data
    view.request = company_request

    with pytest.raises(requests.exceptions.HTTPError):
        view.done()


@patch.object(api_client.company, 'retrieve_private_profile')
def test_company_profile_edit_calls_api(
    mock_retrieve_profile, company_request, api_response_company_profile_200
):

    mock_retrieve_profile.return_value = api_response_company_profile_200
    view = views.CompanyProfileEditView.as_view()

    view(company_request)

    assert mock_retrieve_profile.called_once_with(1)


@patch.object(api_client.company, 'retrieve_private_profile')
def test_company_profile_edit_exposes_api_result_to_form(
    mock_retrieve_profile, company_request, api_response_company_profile_200
):
    mock_retrieve_profile.return_value = api_response_company_profile_200
    view = views.CompanyProfileEditView.as_view()
    expected = api_response_company_profile_200.json()
    expected['sectors'] = expected['sectors'][0]
    response = view(company_request)

    assert response.context_data['form'].initial == expected


@patch.object(api_client.company, 'retrieve_private_profile')
def test_company_profile_edit_handles_bad_api_response(
    mock_retrieve_profile, company_request
):
    mock_retrieve_profile.return_value = create_response(400)
    view = views.CompanyProfileEditView.as_view()

    with pytest.raises(requests.exceptions.HTTPError):
        view(company_request)


def test_company_edit_views_use_correct_template(
    client, rf, sso_user, settings
):
    request = rf.get(reverse('company-edit'))
    request.sso_user = sso_user
    request.session = client.session
    view_class = views.CompanyProfileEditView
    assert view_class.form_list
    for form_pair in view_class.form_list:
        step_name = form_pair[0]
        view = view_class.as_view(form_list=(form_pair,))
        response = view(request)

        assert response.template_name == [view_class.templates[step_name]]


@patch.object(views.CompanyProfileLogoEditView, 'serialize_form_data',
              Mock(return_value={'field': 'value'}))
@patch.object(api_client.company, 'update_profile')
def test_company_profile_logo_api_client_call(mock_update_profile,
                                              company_request):
    view = views.CompanyProfileLogoEditView()
    view.request = company_request
    view.done()
    mock_update_profile.assert_called_once_with(
        sso_session_id='213', data={'field': 'value'}
    )


@patch.object(views.CompanyProfileLogoEditView, 'serialize_form_data',
              Mock(return_value={}))
@patch.object(
    api_client.company, 'update_profile',
    Mock(return_value=create_response(200))
)
def test_company_profile_logo_api_client_success(company_request):
    view = views.CompanyProfileLogoEditView()
    view.request = company_request
    response = view.done()
    assert response.status_code == http.client.FOUND


@patch.object(views.CompanyProfileLogoEditView, 'serialize_form_data',
              Mock(return_value={}))
@patch.object(api_client.company, 'update_profile')
def test_company_profile_logo_api_client_failure(
    mock_update_profile, company_request, settings
):
    mock_update_profile.return_value = create_response(400)

    view = views.CompanyProfileLogoEditView()

    view.request = company_request
    with pytest.raises(requests.exceptions.HTTPError):
        view.done()


@patch.object(
    api_client.company, 'update_profile', return_value=create_response(200)
)
def test_company_profile_edit_create_api_success(
    mock_update_profile, company_profile_edit_end_to_end, sso_user,
    all_company_profile_data, settings
):
    response = company_profile_edit_end_to_end()

    assert response.status_code == 302
    mock_update_profile.assert_called_once_with(
        data={
            'name': all_company_profile_data['name'],
            'website': all_company_profile_data['website'],
            'keywords': all_company_profile_data['keywords'],
            'employees': all_company_profile_data['employees'],
            'sectors': all_company_profile_data['sectors'],
            'export_destinations': (
                all_company_profile_data['export_destinations']
            ),
            'export_destinations_other': (
                all_company_profile_data['export_destinations_other']
            ),
            'has_exported_before': True,
        },
        sso_session_id=sso_user.session_id,
    )


@patch.object(api_client.company, 'update_profile')
def test_company_profile_edit_create_api_failure(
    mock_create_case_study, company_profile_edit_end_to_end,
    settings
):
    mock_create_case_study.return_value = create_response(400)

    with pytest.raises(requests.exceptions.HTTPError):
        company_profile_edit_end_to_end()


def test_company_profile_initial_data_basic(
    company_profile_edit_goto_step, retrieve_profile_data
):
    response = company_profile_edit_goto_step(
        step=views.CompanyProfileEditView.BASIC
    )

    expected = retrieve_profile_data
    expected['sectors'] = expected['sectors'][0]
    assert response.context_data['form'].initial == expected


@patch_check_company_unverified_redirect
def test_send_verification_letter_address_context_data(
    company_profile_edit_goto_step, retrieve_profile_data, has_company_client,
    all_company_profile_data, settings
):
    response = has_company_client.get(reverse('verify-company-address'))

    assert response.context['company_name'] == 'Great company'
    assert response.context['company_number'] == 123456
    assert response.context['company_address'] == (
        '123 Fake Street, Fakeville, London, GB, E14 6XK'
    )


def test_company_profile_initial_data_classification(
    company_profile_edit_goto_step, retrieve_profile_data
):
    response = company_profile_edit_goto_step(
        step=views.CompanyProfileEditView.CLASSIFICATION
    )
    expected = retrieve_profile_data
    expected['sectors'] = expected['sectors'][0]
    assert response.context_data['form'].initial == expected


@patch_check_company_unverified_redirect
@patch.object(
    api_client.company, 'verify_with_code',
    return_value=create_response(200)
)
def test_company_address_validation_api_success(
    mock_verify_with_code, address_verification_end_to_end, sso_user,
    all_address_verification_data, settings
):
    view = views.CompanyAddressVerificationView

    response = address_verification_end_to_end()

    assert response.status_code == http.client.OK
    assert response.template_name == view.templates[view.SUCCESS]
    mock_verify_with_code.assert_called_with(
        code=all_address_verification_data['code'],
        sso_session_id=sso_user.session_id,
    )


@patch_check_company_unverified_redirect
@patch.object(api_client.company, 'verify_with_code')
def test_company_address_validation_api_failure(
    mock_verify_with_code, address_verification_end_to_end
):
    mock_verify_with_code.return_value = create_response(400)

    response = address_verification_end_to_end()
    expected = [validators.MESSAGE_INVALID_CODE]

    assert response.status_code == http.client.OK
    assert response.context_data['form'].errors['code'] == expected


def test_supplier_address_edit_standalone_initial_data(
    retrieve_profile_data, has_company_client, sso_user,
):
    response = has_company_client.get(reverse('company-edit-address'))

    assert response.context_data['form'].initial == {
        **retrieve_profile_data,
        'sectors': retrieve_profile_data['sectors'][0],
    }


@patch.object(
    api_client.company, 'update_profile', return_value=create_response(200)
)
def test_supplier_address_edit_standalone_view_api_success(
    mock_update_profile, has_company_client, supplier_address_data_standalone,
    sso_user,
):

    url = reverse('company-edit-address')
    has_company_client.post(url, supplier_address_data_standalone)

    mock_update_profile.assert_called_once_with(
        sso_session_id=sso_user.session_id,
        data={
            'postal_full_name': 'Jeremy',
        }
    )


def test_supplier_contact_edit_standalone_initial_data(
    has_company_client, retrieve_profile_data
):
    response = has_company_client.get(reverse('company-edit-contact'))

    assert response.context_data['form'].initial == {
        **retrieve_profile_data,
        'sectors': retrieve_profile_data['sectors'][0],
    }


@patch.object(
    api_client.company, 'update_profile', return_value=create_response(200)
)
def test_supplier_contact_edit_standalone_view_api_success(
    mock_update_profile, has_company_client,
    company_profile_contact_standalone_data, sso_user,
):
    url = reverse('company-edit-contact')
    has_company_client.post(url, company_profile_contact_standalone_data)

    mock_update_profile.assert_called_once_with(
        sso_session_id=sso_user.session_id,
        data={
            'email_full_name': 'test',
            'email_address': 'test@example.com',
            'website': 'http://www.example.com',
        }
    )


def test_supplier_sectors_edit_standalone_initial_data(
    has_company_client, retrieve_profile_data
):
    response = has_company_client.get(reverse('company-edit-sectors'))

    assert response.context_data['form'].initial == {
        **retrieve_profile_data,
        'sectors': retrieve_profile_data['sectors'][0],
    }


@patch.object(
    api_client.company, 'update_profile', return_value=create_response(200)
)
def test_supplier_sectors_edit_standalone_view_api_success(
    mock_update_profile, has_company_client,
    company_profile_sectors_standalone_data, sso_user,
):
    url = reverse('company-edit-sectors')
    has_company_client.post(url, company_profile_sectors_standalone_data)
    assert mock_update_profile.call_count == 1
    assert mock_update_profile.call_args == call(
        sso_session_id=sso_user.session_id,
        data={
            'sectors': ['AGRICULTURE_HORTICULTURE_AND_FISHERIES'],
            'export_destinations': ['CN', 'IN'],
            'export_destinations_other': 'West Philadelphia',
            'has_exported_before': True,
        }
    )


@patch.object(
    api_client.company, 'update_profile', return_value=create_response(200)
)
def test_supplier_sectors_edit_standalone_view_api_multiple_sectors(
    mock_update_profile, has_company_client,
    company_profile_sectors_standalone_data, sso_user,
):
    url = reverse('company-edit-sectors')
    has_company_client.post(url, company_profile_sectors_standalone_data)

    assert mock_update_profile.call_count == 1
    assert mock_update_profile.call_args == call(
        sso_session_id=sso_user.session_id,
        data={
            'sectors': ['AGRICULTURE_HORTICULTURE_AND_FISHERIES'],
            'export_destinations': ['CN', 'IN'],
            'export_destinations_other': 'West Philadelphia',
            'has_exported_before': True,
        }
    )


def test_supplier_key_facts_edit_standalone_initial_data(
    has_company_client, retrieve_profile_data
):
    response = has_company_client.get(reverse('company-edit-key-facts'))

    assert response.context_data['form'].initial == {
        **retrieve_profile_data,
        'sectors': retrieve_profile_data['sectors'][0],
    }


@patch.object(
    api_client.company, 'update_profile', return_value=create_response(200)
)
def test_supplier_key_facts_edit_standalone_view_api_success(
    mock_update_profile, has_company_client,
    company_profile_key_facts_standalone_data, sso_user,
):
    url = reverse('company-edit-key-facts')

    has_company_client.post(url, company_profile_key_facts_standalone_data)
    mock_update_profile.assert_called_once_with(
        sso_session_id=sso_user.session_id,
        data={
            'name': 'Example Corp.',
            'website': 'http://www.example.com',
            'keywords': 'Nice, Great',
            'employees': choices.EMPLOYEES[1][0],
        }
    )


def test_supplier_social_links_edit_standalone_initial_data(
    has_company_client, retrieve_profile_data
):
    response = has_company_client.get(reverse('company-edit-social-media'))

    assert response.context_data['form'].initial == {
        **retrieve_profile_data,
        'sectors': retrieve_profile_data['sectors'][0],
    }


@patch.object(
    api_client.company, 'update_profile', return_value=create_response(200)
)
def test_supplier_social_links_edit_standalone_view_api_success(
    mock_update_profile, has_company_client,
    company_profile_social_links_data,
    sso_user, all_social_links_data,
):
    url = reverse('company-edit-social-media')

    has_company_client.post(url, company_profile_social_links_data)

    mock_update_profile.assert_called_once_with(
        sso_session_id=sso_user.session_id,
        data=all_social_links_data,
    )


def test_unsubscribe_logged_in_user(logged_in_client):
    response = logged_in_client.get(reverse('unsubscribe'))

    view = views.EmailUnsubscribeView
    assert response.status_code == http.client.OK
    assert response.template_name == [view.template_name]


def test_unsubscribe_anon_user(client):
    response = client.get(reverse('unsubscribe'))

    assert response.status_code == http.client.FOUND


@patch.object(api_client.supplier, 'unsubscribe')
def test_unsubscribe_api_failure(mock_unsubscribe, logged_in_client):
    logged_in_client.cookies = SimpleCookie(
        {settings.SSO_SESSION_COOKIE: 1}
    )
    mock_unsubscribe.return_value = create_response(400)

    with pytest.raises(requests.exceptions.HTTPError):
        logged_in_client.post(reverse('unsubscribe'))

    mock_unsubscribe.assert_called_once_with(sso_session_id='213')


@patch.object(
    api_client.supplier, 'unsubscribe', return_value=create_response(200)
)
def test_unsubscribe_api_success(mock_unsubscribe, logged_in_client):
    response = logged_in_client.post(reverse('unsubscribe'))

    mock_unsubscribe.assert_called_once_with(sso_session_id='213')
    view = views.EmailUnsubscribeView
    assert response.status_code == http.client.OK
    assert response.template_name == view.success_template


def test_robots(client):
    response = client.get(reverse('robots'))

    assert response.status_code == 200
    assert b'Disallow: /errors/image-too-large/' in response.content


def test_request_payload_too_large(client):
    expected_template_name = views.RequestPaylodTooLargeErrorView.template_name

    response = client.get(
        reverse('request-payload-too-large'),
        {},
        HTTP_REFERER='thing.com',
    )

    assert response.status_code == 200
    assert response.template_name == [expected_template_name]


def test_image_too_large_with_referrer(client):
    # notice absence of the referrer header
    response = client.get(reverse('request-payload-too-large'))

    assert response.status_code == 302
    assert response.url == reverse('index')


def test_company_profile_edit_form_labels_hide_address():
    view = views.CompanyProfileEditView()

    assert view.form_labels == [
        ('basic', 'About your company'),
        ('classification', 'Industry and exporting'),
    ]


@patch_check_company_unverified_redirect
def test_companies_house_oauth2_has_company_redirects(
    settings, has_company_client
):
    url = reverse('verify-companies-house')
    response = has_company_client.get(url)

    assert response.status_code == 302
    assert urllib.parse.unquote_plus(response.url) == (
        'https://account.companieshouse.gov.uk/oauth2/authorise'
        '?client_id=debug-client-id'
        '&redirect_uri=http://testserver/companies-house-oauth2-callback/'
        '&response_type=code'
        '&scope=https://api.companieshouse.gov.uk/company/123456'
    )


@patch_check_company_unverified_redirect
@patch.object(forms.CompaniesHouseClient, 'verify_oauth2_code')
def test_companies_house_callback_missing_code(
    mock_verify_oauth2_code, settings, has_company_client
):
    url = reverse('verify-companies-house-callback')  # missing code
    response = has_company_client.get(url)

    assert response.status_code == 200
    assert mock_verify_oauth2_code.call_count == 0


@patch_check_company_unverified_redirect
@patch.object(forms.CompaniesHouseClient, 'verify_oauth2_code')
@patch.object(
    api_client.company, 'verify_with_companies_house',
    return_value=create_response(200)
)
def test_companies_house_callback_has_company_calls_companies_house(
    mock_verify_with_companies_house, mock_verify_oauth2_code, settings,
    has_company_client, sso_user
):
    mock_verify_oauth2_code.return_value = create_response(
        status_code=200, json_body={'access_token': 'abc'}
    )

    url = reverse('verify-companies-house-callback')
    response = has_company_client.get(url, {'code': '123'})

    assert response.status_code == 302
    assert response.url == str(
        views.CompaniesHouseOauth2CallbackView.success_url
    )

    assert mock_verify_oauth2_code.call_count == 1
    assert mock_verify_oauth2_code.call_args == call(
        code='123',
        redirect_uri='http://testserver/companies-house-oauth2-callback/'
    )

    assert mock_verify_with_companies_house.call_count == 1
    assert mock_verify_with_companies_house.call_args == call(
        sso_session_id=sso_user.session_id,
        access_token='abc',
    )


@patch_check_company_unverified_redirect
@patch.object(forms.CompaniesHouseClient, 'verify_oauth2_code')
@patch.object(
    api_client.company, 'verify_with_companies_house',
    return_value=create_response(200)
)
def test_companies_house_callback_has_company_calls_url_prefix(
    mock_verify_with_companies_house, mock_verify_oauth2_code, settings,
    has_company_client, sso_user
):
    settings.ROOT_URLCONF = 'conf.urls_prefixed'
    settings.FEATURE_URL_PREFIX_ENABLED = True
    mock_verify_oauth2_code.return_value = create_response(
        status_code=200, json_body={'access_token': 'abc'}
    )

    url = reverse('verify-companies-house-callback')
    response = has_company_client.get(url, {'code': '123'})

    assert response.status_code == 302
    assert response.url == str(
        views.CompaniesHouseOauth2CallbackView.success_url
    )

    assert mock_verify_oauth2_code.call_count == 1
    assert mock_verify_oauth2_code.call_args == call(
        code='123',
        redirect_uri=(
            'https://find-a-buyer.export.great.gov.uk/'
            'companies-house-oauth2-callback/'
        )
    )


@patch_check_company_unverified_redirect
@patch.object(forms.CompaniesHouseClient, 'verify_oauth2_code')
@patch.object(
    api_client.company, 'verify_with_companies_house',
    return_value=create_response(500)
)
def test_companies_house_callback_error(
    mock_verify_with_companies_house, mock_verify_oauth2_code, settings,
    has_company_client, sso_user
):
    mock_verify_oauth2_code.return_value = create_response(
        status_code=200, json_body={'access_token': 'abc'}
    )

    url = reverse('verify-companies-house-callback')
    response = has_company_client.get(url, {'code': '123'})

    assert response.status_code == 200
    assert response.template_name == (
        views.CompaniesHouseOauth2CallbackView.error_template
    )


@patch_check_company_unverified_redirect
@patch.object(forms.CompaniesHouseClient, 'verify_oauth2_code')
def test_companies_house_callback_invalid_code(
    mock_verify_oauth2_code, settings, has_company_client
):
    mock_verify_oauth2_code.return_value = create_response(400)

    url = reverse('verify-companies-house-callback')
    response = has_company_client.get(url, {'code': '123'})

    assert response.status_code == 200
    assert b'Invalid code.' in response.content


@patch_check_company_unverified_redirect
@patch.object(forms.CompaniesHouseClient, 'verify_oauth2_code')
def test_companies_house_callback_unauthorized(
    mock_verify_oauth2_code, settings, has_company_client,
):
    mock_verify_oauth2_code.return_value = create_response(401)

    url = reverse('verify-companies-house-callback')
    response = has_company_client.get(url, {'code': '123'})

    assert response.status_code == 200
    assert b'Invalid code.' in response.content


@patch_check_company_unverified_redirect
@patch.object(
    state_requirements.VerificationLetterNotSent, 'is_user_in_required_state',
    Mock(return_value=True)
)
def test_verify_company_has_company_user(
    settings, has_company_client
):
    url = reverse('verify-company-hub')
    response = has_company_client.get(url)

    assert response.status_code == 200
    assert response.template_name == [views.CompanyVerifyView.template_name]


@patch_check_company_unverified_redirect
@patch.object(
    state_requirements.VerificationLetterNotSent, 'is_user_in_required_state',
    Mock(return_value=False)
)
def test_send_letter_redirects_to_enter_code_when_letter_sent(
    has_company_client
):
    url = reverse('verify-company-address')
    response = has_company_client.get(url)

    assert response.status_code == 302
    assert response.url == reverse('verify-company-address-confirm')


@patch_check_company_unverified_redirect
def test_verify_company_address_feature_flag_on(settings, has_company_client):
    response = has_company_client.get(reverse('verify-company-address'))

    assert response.status_code == 200


@patch_check_company_unverified_redirect
@patch.object(api_client.company, 'update_profile')
def test_verify_company_address_end_to_end(
    mock_update_profile, settings, send_verification_letter_end_to_end
):
    mock_update_profile.return_value = create_response(200)
    view = views.SendVerificationLetterView

    response = send_verification_letter_end_to_end()

    assert response.status_code == 200
    assert response.template_name == view.templates[view.SENT]
    assert mock_update_profile.call_count == 1
    assert mock_update_profile.call_args == call(
        data={
            'postal_full_name': 'Jeremy',
        },
        sso_session_id='213'
    )


multi_user_urls = [
    reverse('add-collaborator'),
    reverse('remove-collaborator'),
    reverse('account-transfer'),
]


@pytest.mark.parametrize('url', multi_user_urls)
@patch.object(api_client.company, 'retrieve_collaborators')
def test_multi_user_view_has_company(
    mock_retrieve_collaborators, url, has_company_client,
    api_response_collaborators_200
):
    mock_retrieve_collaborators.return_value = api_response_collaborators_200

    response = has_company_client.get(url)

    assert response.status_code == 200


@patch_check_company_owner_redirect
@patch.object(api_client.company, 'create_collaboration_invite')
def test_add_collaborator_invalid_form(
    mock_create_collaboration_invite, has_company_client
):

    url = reverse('add-collaborator')

    response = has_company_client.post(url, {})

    assert response.status_code == 200
    assert response.context_data['form'].is_valid() is False
    assert 'email_address' in response.context_data['form'].errors

    assert mock_create_collaboration_invite.call_count == 0


@patch_check_company_owner_redirect
@patch.object(
    api_client.company, 'create_collaboration_invite',
    return_value=create_response(200)
)
def test_add_collaborator_valid_form(
    mock_create_collaboration_invite, has_company_client, sso_user
):
    url = reverse('add-collaborator')

    response = has_company_client.post(url, {'email_address': 'a@b.com'})

    assert response.status_code == 302
    assert response.url == (
        'http://profile.trade.great:8006/find-a-buyer/?user-added'
    )

    assert mock_create_collaboration_invite.call_count == 1
    assert mock_create_collaboration_invite.call_args == call(
        sso_session_id=sso_user.session_id,
        collaborator_email='a@b.com'
    )


@patch.object(api_client.company, 'create_collaboration_invite')
def test_add_collaborator_valid_form_already_exists(
    mock_create_collaboration_invite, has_company_client, sso_user
):
    mock_create_collaboration_invite.return_value = create_response(
        400, {'collaborator_email': ['Already exists']}
    )
    url = reverse('add-collaborator')

    response = has_company_client.post(url, {'email_address': 'a@b.com'})

    assert response.status_code == 302
    assert response.get('Location') == (
        'http://profile.trade.great:8006/find-a-buyer/?user-added'
    )


@pytest.mark.parametrize('url,data,mock_path', (
    (
        reverse('add-collaborator'),
        {'email_address': 'a@b.com'},
        'company.views.api_client.company.create_collaboration_invite',
    ),
    (
        reverse('remove-collaborator'),
        {'sso_ids': ['1']},
        'company.views.api_client.company.remove_collaborators',
    )
))
@patch.object(api_client.company, 'retrieve_collaborators')
@patch_check_company_owner_redirect
def test_add_collaborator_valid_form_api_error(
    mock_retrieve_collaborators, url, data, mock_path, has_company_client,
    api_response_collaborators_200
):
    mock_retrieve_collaborators.return_value = api_response_collaborators_200

    with patch(mock_path, return_value=create_response(400)):
        with pytest.raises(requests.exceptions.HTTPError):
            has_company_client.post(url, data)


@patch.object(api_client.company, 'retrieve_collaborators')
@patch.object(api_client.company, 'remove_collaborators')
@patch_check_company_owner_redirect
def test_remove_collaborators_invalid_form(
    mock_remove_collaborators, mock_retrieve_collaborators,
    has_company_client, api_response_collaborators_200
):
    mock_retrieve_collaborators.return_value = api_response_collaborators_200

    url = reverse('remove-collaborator')

    response = has_company_client.post(url, {})

    assert response.status_code == 200
    assert response.context_data['form'].is_valid() is False
    assert 'sso_ids' in response.context_data['form'].errors

    assert mock_remove_collaborators.call_count == 0


@patch.object(api_client.company, 'retrieve_collaborators')
@patch.object(
    api_client.company, 'remove_collaborators',
    return_value=create_response(200)
)
@patch_check_company_owner_redirect
def test_remove_collaborators_valid_form(
    mock_remove_collaborators, mock_retrieve_collaborators,
    has_company_client, api_response_collaborators_200, sso_user
):
    mock_retrieve_collaborators.return_value = api_response_collaborators_200

    url = reverse('remove-collaborator')

    response = has_company_client.post(url, {'sso_ids': ['1']})

    assert response.status_code == 302
    assert response.url == (
        'http://profile.trade.great:8006/find-a-buyer/?user-removed'
    )

    assert mock_remove_collaborators.call_count == 1
    assert mock_remove_collaborators.call_args == call(
        sso_session_id=sso_user.session_id,
        sso_ids=['1']
    )


@patch.object(api_client.company, 'create_transfer_invite')
def test_transfer_owner_invalid_form(
    ock_create_transfer_invite, has_company_client
):
    view = views.TransferAccountWizardView

    response = has_company_client.post(
        reverse('account-transfer'),
        {
            'transfer_account_wizard_view-current_step': view.EMAIL,
            view.EMAIL + '-email_address': 'a.com'
        }
    )

    assert response.status_code == 200
    assert response.context_data['form'].is_valid() is False
    assert 'email_address' in response.context_data['form'].errors

    assert ock_create_transfer_invite.call_count == 0


def test_company_address_verification_backwards_compatible_feature_flag_on(
    settings, client
):
    url = reverse('verify-company-address-historic-url')
    response = client.get(url)

    assert response.status_code == 302
    assert response.get('Location') == reverse('verify-company-address')


@patch.object(api_client.company, 'create_transfer_invite')
@patch.object(forms.sso_api_client.user, 'check_password')
@patch_check_company_owner_redirect
def test_transfer_owner_invalid_password(
    mock_check_password, mock_create_transfer_invite, has_company_client,
    sso_user
):
    mock_check_password.return_value = create_response(400)

    view = views.TransferAccountWizardView

    has_company_client.post(
        reverse('account-transfer'),
        {
            'transfer_account_wizard_view-current_step': view.EMAIL,
            view.EMAIL + '-email_address': 'a@b.com'
        }
    )
    response = has_company_client.post(
        reverse('account-transfer'),
        {
            'transfer_account_wizard_view-current_step': view.PASSWORD,
            view.PASSWORD + '-password': 'password'
        }
    )

    expected_error = forms.TransferAccountPasswordForm.MESSAGE_INVALID_PASSWORD
    assert response.status_code == 200
    assert response.context_data['form'].errors['password'] == [expected_error]

    assert mock_create_transfer_invite.call_count == 0


@patch.object(api_client.company, 'create_transfer_invite')
@patch(
    'company.forms.sso_api_client.user.check_password',
    Mock(return_value=create_response(200))
)
@patch_check_company_owner_redirect
def test_transfer_owner_valid_form(
    mock_create_transfer_invite, has_company_client, sso_user
):
    view = views.TransferAccountWizardView

    has_company_client.post(
        reverse('account-transfer'),
        {
            'transfer_account_wizard_view-current_step': view.EMAIL,
            view.EMAIL + '-email_address': 'a@b.com'
        }
    )
    response = has_company_client.post(
        reverse('account-transfer'),
        {
            'transfer_account_wizard_view-current_step': view.PASSWORD,
            view.PASSWORD + '-password': 'password'
        }
    )

    assert response.status_code == 302
    assert response.url == (
        'http://profile.trade.great:8006/find-a-buyer/?owner-transferred'
    )
    assert mock_create_transfer_invite.call_count == 1
    assert mock_create_transfer_invite.call_args == call(
        sso_session_id=sso_user.session_id, new_owner_email='a@b.com'
    )


@patch.object(api_client.company, 'create_transfer_invite')
@patch.object(forms.sso_api_client.user, 'check_password')
@patch_check_company_owner_redirect
def test_transfer_owner_valid_form_already_exists(
    mock_check_password, mock_create_transfer_invite, has_company_client,
    sso_user
):
    mock_check_password.return_value = mock_create_transfer_invite
    mock_create_transfer_invite.return_value = create_response(
        http.client.BAD_REQUEST, {'new_owner_email': ['Already exists']}
    )

    view = views.TransferAccountWizardView

    has_company_client.post(
        reverse('account-transfer'),
        {
            'transfer_account_wizard_view-current_step': view.EMAIL,
            view.EMAIL + '-email_address': 'a@b.com'
        }
    )
    response = has_company_client.post(
        reverse('account-transfer'),
        {
            'transfer_account_wizard_view-current_step': view.PASSWORD,
            view.PASSWORD + '-password': 'password'
        }
    )

    assert response.status_code == 302
    assert response.url == (
        'http://profile.trade.great:8006/find-a-buyer/?owner-transferred'
    )


@patch.object(api_client.company, 'create_transfer_invite')
@patch(
    'company.forms.sso_api_client.user.check_password',
    return_value=create_response(200)
)
@patch_check_company_owner_redirect
def test_transfer_owner_valid_form_api_error(
    mock_check_password, mock_create_transfer_invite, has_company_client
):
    mock_create_transfer_invite.return_value = create_response(400)

    view = views.TransferAccountWizardView
    url = reverse('account-transfer')

    has_company_client.post(
        reverse('account-transfer'),
        {
            'transfer_account_wizard_view-current_step': view.EMAIL,
            view.EMAIL + '-email_address': 'a@b.com'
        }
    )
    with pytest.raises(requests.exceptions.HTTPError):
        has_company_client.post(
            url,
            {
                'transfer_account_wizard_view-current_step': view.PASSWORD,
                view.PASSWORD + '-password': 'password'
            }
        )


invite_urls = (
    reverse('account-transfer-accept'),
    reverse('account-collaborate-accept'),
)


@patch('company.views.AcceptTransferAccountView.retrieve_api_method')
@patch_check_not_company_owner_redirect
def test_accept_ownership_invite_get_invite(
    mock_retrieve_api_method, logged_in_client, api_response_get_invite_200
):
    url = reverse('account-transfer-accept')
    mock_retrieve_api_method.return_value = api_response_get_invite_200
    response = logged_in_client.get(url)

    assert response.status_code == 200
    assert response.context_data['invite'] == {'company_name': 'A Company'}


@patch('company.views.AcceptCollaborationView.retrieve_api_method')
@patch_check_no_company_redirect
def test_accept_collaborate_invite_get_invite(
    mock_retrieve_api_method, logged_in_client, api_response_get_invite_200
):
    url = reverse('account-collaborate-accept')
    mock_retrieve_api_method.return_value = api_response_get_invite_200
    response = logged_in_client.get(url)

    assert response.status_code == 200
    assert response.context_data['invite'] == {'company_name': 'A Company'}


@patch('company.views.AcceptTransferAccountView.retrieve_api_method')
@patch_check_not_company_owner_redirect
def test_accept_ownership_invite_no_invite_key(
    mock_retrieve_api_method, logged_in_client, api_response_get_invite_200
):
    url = reverse('account-transfer-accept')
    mock_retrieve_api_method.return_value = api_response_get_invite_200
    response = logged_in_client.post(url, data={})

    assert response.status_code == 200
    assert response.context_data['form'].is_valid() is False
    assert 'invite_key' in response.context_data['form'].errors


@patch('company.views.AcceptCollaborationView.retrieve_api_method')
@patch_check_no_company_redirect
def test_accept_collaborate_invite_no_invite_key(
    mock_retrieve_api_method, logged_in_client, api_response_get_invite_200
):
    url = reverse('account-collaborate-accept')
    mock_retrieve_api_method.return_value = api_response_get_invite_200
    response = logged_in_client.post(url, data={})

    assert response.status_code == 200
    assert response.context_data['form'].is_valid() is False
    assert 'invite_key' in response.context_data['form'].errors


@patch('company.views.AcceptTransferAccountView.retrieve_api_method')
@patch(
    'company.views.AcceptTransferAccountView.accept_api_method',
    Mock(return_value=create_response(200))
)
@patch_check_not_company_owner_redirect
def test_accept_ownership_invite_valid_invite_key(
    mock_retrieve_api_method, logged_in_client, api_response_get_invite_200
):
    mock_retrieve_api_method.return_value = api_response_get_invite_200
    url = reverse('account-transfer-accept')

    response = logged_in_client.post(url, data={'invite_key': '123'})

    assert response.status_code == 302
    assert response.url == reverse('company-detail')


@patch('company.views.AcceptCollaborationView.retrieve_api_method')
@patch(
    'company.views.AcceptCollaborationView.accept_api_method',
    Mock(return_value=create_response(200))
)
@patch_check_no_company_redirect
def test_accept_collaborate_invite_valid_invite_key(
    mock_retrieve_api_method, logged_in_client, api_response_get_invite_200
):
    mock_retrieve_api_method.return_value = api_response_get_invite_200
    url = reverse('account-collaborate-accept')

    response = logged_in_client.post(url, data={'invite_key': '123'})

    assert response.status_code == 302
    assert response.url == reverse('company-detail')


@patch_check_not_company_owner_redirect
@patch('company.views.AcceptTransferAccountView.retrieve_api_method')
def test_accept_invite_transfer_invite_key_invalid(
    mock_retrieve_api_method, has_company_client
):
    mock_retrieve_api_method.return_value = create_response(400)
    url = reverse('account-transfer-accept')

    response = has_company_client.get(url)

    assert response.status_code == 200
    assert response.context_data['invite'] is None


@patch_check_no_company_redirect
@patch('company.views.AcceptCollaborationView.retrieve_api_method')
def test_accept_invite_collaborate_invitekey_invalid(
    mock_retrieve_api_method, logged_in_client
):
    url = reverse('account-collaborate-accept')
    mock_retrieve_api_method.return_value = create_response(400)

    response = logged_in_client.get(url)

    assert response.status_code == 200
    assert response.context_data['invite'] is None


def test_case_study_create_backwards_compatible_url(client):
    url = reverse('company-case-study-create-backwards-compatible')
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == reverse('company-case-study-create')


def test_buyer_csv_dump_no_token(client):
    url = reverse('buyers-csv-dump')
    response = client.get(url)

    assert response.status_code == 403
    assert response.content == b'Token not provided'


@patch('company.views.api_client')
def test_buyer_csv_dump(mocked_api_client, client):
    mocked_api_client.buyer.get_csv_dump.return_value = Mock(
        content='abc',
        headers={
            'Content-Type': 'foo',
            'Content-Disposition': 'bar'
        }
    )
    url = reverse('buyers-csv-dump')
    response = client.get(url+'?token=debug')
    assert mocked_api_client.buyer.get_csv_dump.called is True
    assert mocked_api_client.buyer.get_csv_dump.called_once_with(token='debug')
    assert response.content == b'abc'
    assert response._headers['content-type'] == ('Content-Type', 'foo')
    assert response._headers['content-disposition'] == (
        'Content-Disposition', 'bar'
    )


@patch('company.views.api_client')
def test_supplier_csv_dump(mocked_api_client, client):
    mocked_api_client.supplier.get_csv_dump.return_value = Mock(
        content='abc',
        headers={
            'Content-Type': 'foo',
            'Content-Disposition': 'bar'
        }
    )
    url = reverse('suppliers-csv-dump')
    response = client.get(url+'?token=debug')
    assert mocked_api_client.supplier.get_csv_dump.called is True
    assert mocked_api_client.supplier.get_csv_dump.called_once_with(
        token='debug'
    )
    assert response.content == b'abc'
    assert response._headers['content-type'] == ('Content-Type', 'foo')
    assert response._headers['content-disposition'] == (
        'Content-Disposition', 'bar'
    )


@patch.object(api_client.company, 'retrieve_private_profile')
def test_company_profile_mixin_404(mock_retrieve_profile, rf):
    mock_retrieve_profile.return_value = create_response(404)

    class TestView(views.CompanyProfileMixin, TemplateView):
        template_name = 'company-profile-detail.html'

        def get_context_data(self, *args, **kwargs):
            return {'company_profile': self.company_profile}

    request = rf.get('/')
    request.sso_user = Mock()
    view = TestView.as_view()

    response = view(request)
    assert response.context_data['company_profile'] == {}


@patch.object(api_client.supplier, 'retrieve_profile')
def test_supplier_profile_mixin_404(mock_retrieve_profile, rf):
    mock_retrieve_profile.return_value = create_response(404)

    class TestView(views.SupplierProfileMixin, TemplateView):
        template_name = 'company-profile-detail.html'

        def get_context_data(self, *args, **kwargs):
            return {'supplier_profile': self.supplier_profile}

    request = rf.get('/')
    request.sso_user = Mock()
    view = TestView.as_view()

    response = view(request)
    assert response.context_data['supplier_profile'] == {}


@pytest.mark.parametrize('view_class,expected', [
    (
        views.SupplierCaseStudyWizardView,
        [state_requirements.IsLoggedIn, state_requirements.HasCompany]
    ),
    (
        views.CompanyProfileDetailView,
        [state_requirements.IsLoggedIn, state_requirements.HasCompany]
    ),
    (
        views.CompanyProfileEditView,
        [state_requirements.IsLoggedIn, state_requirements.HasCompany]
    ),
    (
        views.CompanyProfileLogoEditView,
        [state_requirements.IsLoggedIn, state_requirements.HasCompany]
    ),
    (
        views.CompanyDescriptionEditView,
        [state_requirements.IsLoggedIn, state_requirements.HasCompany]
    ),
    (
        views.CompanySocialLinksEditView,
        [state_requirements.IsLoggedIn, state_requirements.HasCompany]
    ),
    (
        views.SupplierBasicInfoEditView,
        [state_requirements.IsLoggedIn, state_requirements.HasCompany]
    ),
    (
        views.SupplierClassificationEditView,
        [state_requirements.IsLoggedIn, state_requirements.HasCompany]
    ),
    (
        views.SupplierContactEditView,
        [state_requirements.IsLoggedIn, state_requirements.HasCompany]
    ),
    (
        views.SupplierAddressEditView,
        [state_requirements.IsLoggedIn, state_requirements.HasCompany]
    ),
    (
        views.SendVerificationLetterView,
        [
            state_requirements.IsLoggedIn,
            state_requirements.HasUnverifiedCompany,
            state_requirements.VerificationLetterNotSent
        ]
    ),
    (
        views.CompanyVerifyView,
        [
            state_requirements.IsLoggedIn,
            state_requirements.HasUnverifiedCompany,
            state_requirements.VerificationLetterNotSent,
        ]
    ),
    (
        views.CompanyAddressVerificationView,
        [
            state_requirements.IsLoggedIn,
            state_requirements.HasUnverifiedCompany
        ]
    ),
    (
        views.EmailUnsubscribeView,
        [state_requirements.IsLoggedIn]
    ),
    (
        views.CompaniesHouseOauth2View,
        [
            state_requirements.IsLoggedIn,
            state_requirements.HasUnverifiedCompany,
        ]
    ),
    (
        views.CompaniesHouseOauth2CallbackView,
        [
            state_requirements.IsLoggedIn,
            state_requirements.HasUnverifiedCompany,
        ]
    ),
    (
        views.AddCollaboratorView,
        [state_requirements.IsLoggedIn, state_requirements.IsCompanyOwner]
    ),
    (
        views.RemoveCollaboratorView,
        [state_requirements.IsLoggedIn, state_requirements.IsCompanyOwner]
    ),
    (
        views.TransferAccountWizardView,
        [state_requirements.IsLoggedIn, state_requirements.IsCompanyOwner]
    ),
    (
        views.AcceptTransferAccountView,
        [state_requirements.IsLoggedIn, state_requirements.NotCompanyOwner]
    ),
    (
        views.AcceptCollaborationView,
        [state_requirements.IsLoggedIn, state_requirements.NoCompany]
    ),
])
def test_required_user_states(view_class, expected):
    mixin_class = state_requirements.UserStateRequirementHandlerMixin
    assert issubclass(view_class, mixin_class)
    for rule in expected:
        assert rule in view_class.required_user_states
