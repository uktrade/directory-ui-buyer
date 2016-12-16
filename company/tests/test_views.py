import http
from unittest.mock import patch, Mock

from directory_validators.constants import choices
import pytest
import requests

from django.core.urlresolvers import reverse

from sso.utils import SSOUser
from company import forms, helpers, views, validators


default_sector = choices.COMPANY_CLASSIFICATIONS[1][0]


class Wildcard:
    def __eq__(*args, **kwargs):
        return True


@pytest.fixture
def api_response_200():
    response = requests.Response()
    response.status_code = http.client.OK
    return response


@pytest.fixture
def api_response_400():
    response = requests.Response()
    response.status_code = http.client.BAD_REQUEST
    return response


@pytest.fixture
def api_response_404(*args, **kwargs):
    response = requests.Response()
    response.status_code = http.client.NOT_FOUND
    return response


@pytest.fixture
def retrieve_supplier_case_study_200(api_response_200):
    response = api_response_200
    response.json = lambda: {'field': 'value'}
    return response


def process_request(self, request):
    request.sso_user = sso_user()


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
        'testimonial_name': 'Neville',
        'testimonial_job_title': 'Abstract hat maker',
        'testimonial_company': 'Imaginary hats Ltd',
        'image_one': image_one,
        'image_two': image_two,
        'image_three': image_three,
    }


@pytest.fixture
def supplier_case_study_basic_data():
    view = views.SupplierCaseStudyWizardView
    return {
        'supplier_case_study_wizard_view-current_step': view.BASIC,
        view.BASIC + '-title': 'Example',
        view.BASIC + '-description': 'Great',
        view.BASIC + '-sector': default_sector,
        view.BASIC + '-website': 'http://www.example.com',
        view.BASIC + '-year': '2000',
        view.BASIC + '-keywords': 'good, great'
    }


@pytest.fixture
def supplier_case_study_rich_data(image_three, image_two, image_one):
    view = views.SupplierCaseStudyWizardView
    return {
        'supplier_case_study_wizard_view-current_step': view.RICH_MEDIA,
        view.RICH_MEDIA + '-image_one': image_one,
        view.RICH_MEDIA + '-image_two': image_two,
        view.RICH_MEDIA + '-image_three': image_three,
        view.RICH_MEDIA + '-testimonial': 'Great',
        view.RICH_MEDIA + '-testimonial_name': 'Neville',
        view.RICH_MEDIA + '-testimonial_job_title': 'Abstract hat maker',
        view.RICH_MEDIA + '-testimonial_company': 'Imaginary hats Ltd',
    }


@pytest.fixture
def all_company_profile_data():
    return {
        'name': 'Example Corp.',
        'website': 'http://www.example.com',
        'keywords': 'Nice, Great',
        'employees': choices.EMPLOYEES[1][0],
        'sectors': [choices.COMPANY_CLASSIFICATIONS[1][0]],
        'contact_details': {
            'mobile_number': '07555555555',
            'email_full_name': 'Jeremy',
            'email_address': 'test@example.com',
            'postal_full_name': 'Jeremy',
            'address_line_1': '123 Fake Street',
            'address_line_2': 'Fakeville',
            'locality': 'London',
            'postal_code': 'E14 6XK',
            'po_box': 'abc',
            'country': 'GB',
        },
    }


@pytest.fixture
def company_profile_address_data(all_company_profile_data):
    view = views.SupplierCompanyProfileEditView
    data = all_company_profile_data['contact_details']
    return {
        'supplier_company_profile_edit_view-current_step': view.ADDRESS,
        view.ADDRESS + '-postal_full_name': data['postal_full_name'],
        view.ADDRESS + '-address_line_1': data['address_line_1'],
        view.ADDRESS + '-address_line_2': data['address_line_2'],
        view.ADDRESS + '-locality': data['locality'],
        view.ADDRESS + '-postal_code': data['postal_code'],
        view.ADDRESS + '-po_box': data['po_box'],
        view.ADDRESS + '-country': data['country'],
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
    view = views.SupplierCompanyProfileEditView
    data = all_company_profile_data
    return {
        'supplier_company_profile_edit_view-current_step': view.BASIC,
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
    view = views.SupplierCompanyProfileEditView
    data = all_company_profile_data
    return {
        'supplier_company_profile_edit_view-current_step': view.CLASSIFICATION,
        view.CLASSIFICATION + '-sectors': data['sectors'],
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
def company_profile_contact_data(all_company_profile_data):
    view = views.SupplierCompanyProfileEditView
    data = all_company_profile_data['contact_details']
    return {
        'supplier_company_profile_edit_view-current_step': view.CONTACT,
        view.CONTACT + '-email_address': data['email_address'],
        view.CONTACT + '-email_full_name': data['email_full_name'],
        view.CONTACT + '-mobile_number': data['mobile_number'],
    }


@pytest.fixture
def company_profile_contact_standalone_data(company_profile_contact_data):
    data = company_profile_contact_data
    step = views.SupplierContactEditView.CONTACT
    data['supplier_contact_edit_view-current_step'] = step
    return data


@pytest.fixture
def all_address_verification_data():
    return {
        'code': 'x'*12
    }


@pytest.fixture
def address_verification_address_data(all_address_verification_data):
    view = views.SupplierCompanyAddressVerificationView
    data = all_address_verification_data
    step = view.ADDRESS
    return {
        'supplier_company_address_verification_view-current_step': step,
        step + '-code': data['code'],
    }


@pytest.fixture
def supplier_case_study_end_to_end(
    client, supplier_case_study_basic_data, supplier_case_study_rich_data
):
    # loop over each step in the supplier case study wizard and post valid data
    view = views.SupplierCaseStudyWizardView
    data_step_pairs = [
        [view.BASIC, supplier_case_study_basic_data],
        [view.RICH_MEDIA, supplier_case_study_rich_data],
    ]

    def inner(case_study_id=''):
        url = reverse('company-case-study-edit', kwargs={'id': case_study_id})
        for key, data in data_step_pairs:
            response = client.post(url, data)
        return response
    return inner


@pytest.fixture
def address_verification_end_to_end(client, address_verification_address_data):
    view = views.SupplierCompanyAddressVerificationView
    data_step_pairs = [
        [view.ADDRESS, address_verification_address_data],
    ]

    def inner(case_study_id=''):
        url = reverse('confirm-company-address')
        for key, data in data_step_pairs:
            response = client.post(url, data)
        return response
    return inner


@pytest.fixture
def company_profile_edit_end_to_end(
    client, company_profile_address_data,
    company_profile_basic_data, company_profile_classification_data,
    company_profile_contact_data, api_response_200
):
    # loop over each step in the supplier case study wizard and post valid data
    view = views.SupplierCompanyProfileEditView
    data_step_pairs = [
        [view.BASIC, company_profile_basic_data],
        [view.CLASSIFICATION, company_profile_classification_data],
        [view.CONTACT, company_profile_contact_data],
        [view.ADDRESS, company_profile_address_data],
    ]

    def inner():
        url = reverse('company-edit')
        for key, data in data_step_pairs:
            response = client.post(url, data)
        return response
    return inner


@pytest.fixture
def company_profile_edit_goto_step(
    client, company_profile_address_data,
    company_profile_basic_data, company_profile_classification_data,
    company_profile_contact_data, api_response_200
):
    # loop over each step in the supplier case study wizard and post valid data
    view = views.SupplierCompanyProfileEditView
    data_step_pairs = [
        [view.BASIC, company_profile_basic_data],
        [view.CLASSIFICATION, company_profile_classification_data],
        [view.CONTACT, company_profile_contact_data],
        [view.ADDRESS, company_profile_address_data],
    ]

    def inner(step=view.ADDRESS):
        index = next(
            data_step_pairs.index(item)
            for item in data_step_pairs
            if item[0] == step
        )
        url = reverse('company-edit')
        if index == 0:
            response = client.get(url)
        else:
            for key, data in data_step_pairs[:index]:
                response = client.post(url, data, follow=True)
        return response
    return inner


@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch.object(views, 'has_company', Mock(return_value=True))
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
@patch.object(views, 'has_company', Mock(return_value=True))
@patch('api_client.api_client.company.retrieve_supplier_case_study')
def test_case_study_edit_exposes_api_response_data(
    mock_retrieve_case_study, client, retrieve_supplier_case_study_200
):
    mock_retrieve_case_study.return_value = retrieve_supplier_case_study_200

    url = reverse('company-case-study-edit', kwargs={'id': '2'})
    response = client.get(url)

    assert response.context['form'].initial == {'field': 'value'}


@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch.object(views, 'has_company', Mock(return_value=True))
@patch('api_client.api_client.company.retrieve_supplier_case_study')
def test_case_study_edit_handles_api_error(
    mock_retrieve_case_study, client, api_response_400
):
    mock_retrieve_case_study.return_value = api_response_400

    url = reverse('company-case-study-edit', kwargs={'id': '2'})
    with pytest.raises(requests.exceptions.HTTPError):
        client.get(url)


@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch.object(views, 'has_company', Mock(return_value=True))
@patch.object(views.api_client.company, 'create_supplier_case_study')
def test_case_study_create_api_success(
    mock_create_case_study, supplier_case_study_end_to_end, sso_user,
    all_case_study_data, api_response_200
):
    mock_create_case_study.return_value = api_response_200

    response = supplier_case_study_end_to_end()

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == reverse('company-detail')
    mock_create_case_study.assert_called_once_with(
        data=all_case_study_data,
        sso_user_id=sso_user.id,
    )


@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch.object(views, 'has_company', Mock(return_value=True))
@patch.object(views.api_client.company, 'create_supplier_case_study')
def test_case_study_create_api_failure(
    mock_create_case_study, supplier_case_study_end_to_end, api_response_400
):
    mock_create_case_study.return_value = api_response_400

    response = supplier_case_study_end_to_end()

    view = views.SupplierCaseStudyWizardView
    assert response.status_code == http.client.OK
    assert response.template_name == view.failure_template


@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch.object(views, 'has_company', Mock(return_value=True))
@patch.object(views.api_client.company, 'update_supplier_case_study')
def test_case_study_update_api_success(
    mock_update_case_study, supplier_case_study_end_to_end, sso_user,
    all_case_study_data, api_response_200
):
    mock_update_case_study.return_value = api_response_200

    response = supplier_case_study_end_to_end(case_study_id='1')

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == reverse('company-detail')
    mock_update_case_study.assert_called_once_with(
        data=all_case_study_data,
        case_study_id='1',
        sso_user_id=sso_user.id,
    )


@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch.object(views, 'has_company', Mock(return_value=True))
@patch.object(views.api_client.company, 'update_supplier_case_study')
def test_case_study_update_api_failure(
    mock_update_case_study, supplier_case_study_end_to_end, api_response_400
):
    mock_update_case_study.return_value = api_response_400

    response = supplier_case_study_end_to_end(case_study_id='1')

    view = views.SupplierCaseStudyWizardView
    assert response.status_code == http.client.OK
    assert response.template_name == view.failure_template


@patch.object(views, 'has_company', Mock(return_value=True))
@patch.object(helpers, 'get_company_profile_from_response')
@patch.object(forms, 'is_optional_profile_values_set', return_value=True)
def test_company_profile_details_exposes_context(
    mock_is_optional_profile_values_set,
    mock_get_company_profile_from_response, sso_request
):
    company = {'key': 'value'}
    mock_get_company_profile_from_response.return_value = company
    view = views.SupplierCompanyProfileDetailView.as_view()
    response = view(sso_request)
    assert response.status_code == http.client.OK
    assert response.template_name == [
        views.SupplierCompanyProfileDetailView.template_name
    ]

    assert response.context_data['company'] == company
    assert response.context_data['show_wizard_links'] is False
    mock_is_optional_profile_values_set.assert_called_once_with(company)


@patch.object(views, 'has_company', Mock(return_value=True))
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


@patch.object(views, 'has_company', Mock(return_value=True))
@patch.object(helpers, 'get_company_profile_from_response')
@patch.object(views.api_client.company, 'retrieve_profile')
def test_company_profile_details_handles_bad_status(
    mock_retrieve_profile, mock_get_company_profile_from_response,
    sso_request, api_response_400
):
    mock_retrieve_profile.return_value = api_response_400
    mock_get_company_profile_from_response.return_value = {}
    view = views.SupplierCompanyProfileDetailView.as_view()

    with pytest.raises(requests.exceptions.HTTPError):
        view(sso_request)


@patch.object(views, 'has_company', Mock(return_value=True))
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


@patch.object(views, 'has_company', Mock(return_value=True))
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


@patch.object(views, 'has_company', Mock(return_value=True))
@patch.object(helpers, 'get_public_company_profile_from_response')
@patch.object(views.api_client.company,
              'retrieve_public_profile_by_companies_house_number')
def test_public_company_profile_details_handles_bad_status(
    mock_retrieve_public_profile,
    mock_get_public_company_profile_from_response, client, api_response_400
):
    mock_retrieve_public_profile.return_value = api_response_400
    url = reverse(
        'public-company-profiles-detail', kwargs={'company_number': '01234567'}
    )

    with pytest.raises(requests.exceptions.HTTPError):
        client.get(url)


@patch.object(views, 'has_company', Mock(return_value=True))
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


@patch.object(views, 'has_company', Mock(return_value=True))
def test_company_profile_list_exposes_selected_sector_label(client):
    url = reverse('public-company-profiles-list')
    params = {'sectors': choices.COMPANY_CLASSIFICATIONS[1][0]}
    response = client.get(url, params)

    expected_label = choices.COMPANY_CLASSIFICATIONS[1][1]
    assert response.context_data['selected_sector_label'] == expected_label


@patch.object(views, 'has_company', Mock(return_value=True))
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


@patch.object(views, 'has_company', Mock(return_value=True))
@patch.object(views.api_client.company, 'list_public_profiles')
def test_company_profile_list_handles_bad_status(
    mock_retrieve_public_profile, client, api_response_400
):
    mock_retrieve_public_profile.return_value = api_response_400
    url = reverse('public-company-profiles-list')
    params = {'sectors': choices.COMPANY_CLASSIFICATIONS[1][0]}
    with pytest.raises(requests.exceptions.HTTPError):
        client.get(url, params)


@patch.object(views, 'has_company', Mock(return_value=True))
def test_company_profile_list_handles_no_form_data(client):
    url = reverse('public-company-profiles-list')
    response = client.get(url, {})

    assert response.context_data['form'].errors == {}


@patch.object(views, 'has_company', Mock(return_value=True))
@patch.object(views.api_client.company, 'list_public_profiles')
def test_company_profile_list_handles_empty_page(mock_list_profiles, client):
    mock_list_profiles.return_value = api_response_404()
    url = reverse('public-company-profiles-list')
    response = client.get(url, {'sectors': 'WATER', 'page': 10})

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == '{url}?sectors=WATER'.format(url=url)


@patch.object(views, 'has_company', Mock(return_value=True))
@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch.object(views.api_client.company, 'retrieve_supplier_case_study')
def test_supplier_case_study_exposes_context(
    mock_retrieve_supplier_case_study, client,
    api_response_retrieve_supplier_case_study_200
):
    mock_retrieve_supplier_case_study.return_value = (
        api_response_retrieve_supplier_case_study_200
    )
    expected_case_study = helpers.get_case_study_details_from_response(
        api_response_retrieve_supplier_case_study_200
    )
    url = reverse('company-case-study-view', kwargs={'id': '2'})
    response = client.get(url)

    assert response.status_code == http.client.OK
    assert response.template_name == [
        views.SupplierCaseStudyDetailView.template_name
    ]
    assert response.context_data['case_study'] == expected_case_study


@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch.object(views, 'has_company', Mock(return_value=True))
@patch.object(views.api_client.company, 'retrieve_supplier_case_study')
def test_supplier_case_study_calls_api(
    mock_retrieve_supplier_case_study, client,
    api_response_retrieve_supplier_case_study_200
):
    mock_retrieve_supplier_case_study.return_value = (
        api_response_retrieve_supplier_case_study_200
    )
    url = reverse('company-case-study-view', kwargs={'id': '2'})
    client.get(url)

    assert mock_retrieve_supplier_case_study.called_once_with(pk='2')


@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch.object(views, 'has_company', Mock(return_value=True))
@patch.object(views.api_client.company, 'retrieve_supplier_case_study')
def test_supplier_case_study_handles_bad_status(
    mock_retrieve_supplier_case_study, client, api_response_400
):
    mock_retrieve_supplier_case_study.return_value = api_response_400
    url = reverse('company-case-study-view', kwargs={'id': '2'})

    with pytest.raises(requests.exceptions.HTTPError):
        client.get(url)


@patch.object(views, 'has_company', Mock(return_value=True))
@patch.object(views.SupplierCompanyDescriptionEditView, 'serialize_form_data',
              Mock(return_value={'field': 'value'}))
@patch.object(views.api_client.company, 'update_profile')
def test_company_profile_description_api_client_call(mock_update_profile,
                                                     company_request):

    view = views.SupplierCompanyDescriptionEditView()
    view.request = company_request
    view.done()
    mock_update_profile.assert_called_once_with(
        sso_user_id=1, data={'field': 'value'}
    )


@patch.object(views, 'has_company', Mock(return_value=True))
@patch.object(views.SupplierCompanyDescriptionEditView, 'serialize_form_data',
              Mock(return_value={}))
@patch.object(views.api_client.company, 'update_profile')
def test_company_profile_description_api_client_success(
    mock_update_profile, company_request, api_response_200
):
    mock_update_profile.return_value = api_response_200

    view = views.SupplierCompanyDescriptionEditView()
    view.request = company_request
    response = view.done()
    assert response.status_code == http.client.FOUND


@patch.object(views, 'has_company', Mock(return_value=True))
@patch.object(views.SupplierCompanyDescriptionEditView, 'serialize_form_data',
              Mock(return_value={}))
@patch.object(views.api_client.company, 'update_profile')
def test_company_profile_description_api_client_failure(
    mock_update_profile, company_request, api_response_400
):
    mock_update_profile.return_value = api_response_400

    view = views.SupplierCompanyDescriptionEditView()
    view.request = company_request
    response = view.done()
    assert response.status_code == http.client.OK
    expected_template_name = (
        views.SupplierCompanyDescriptionEditView.failure_template
    )
    assert response.template_name == expected_template_name


@patch.object(views, 'has_company', Mock(return_value=True))
@patch.object(views.api_client.company, 'retrieve_profile')
def test_company_description_edit_calls_api(
    mock_retrieve_profile, company_request, api_response_company_profile_200
):
    mock_retrieve_profile.return_value = api_response_company_profile_200
    view = views.SupplierCompanyDescriptionEditView.as_view()

    view(company_request)

    assert mock_retrieve_profile.called_once_with(1)


@patch.object(views, 'has_company', Mock(return_value=True))
@patch.object(views.api_client.company, 'retrieve_profile')
def test_company_profile_description_exposes_api_result_to_form(
    mock_retrieve_profile, company_request, api_response_company_profile_200
):
    mock_retrieve_profile.return_value = api_response_company_profile_200
    view = views.SupplierCompanyDescriptionEditView.as_view()
    expected = api_response_company_profile_200.json()

    response = view(company_request)

    assert response.context_data['form'].initial == expected


@patch.object(views, 'has_company', Mock(return_value=True))
@patch.object(views.api_client.company, 'retrieve_profile')
def test_company_description_edit_handles_bad_api_response(
    mock_retrieve_profile, company_request, api_response_400
):

    mock_retrieve_profile.return_value = api_response_400
    view = views.SupplierCompanyDescriptionEditView.as_view()

    with pytest.raises(requests.exceptions.HTTPError):
        view(company_request)


@patch.object(views, 'has_company', Mock(return_value=True))
def test_company_description_edit_views_use_correct_template(
        client, rf, sso_user):
    request = rf.get(reverse('company-edit-description'))
    request.sso_user = sso_user
    request.session = client.session
    view_class = views.SupplierCompanyDescriptionEditView
    assert view_class.form_list
    for form_pair in view_class.form_list:
        step_name = form_pair[0]
        view = view_class.as_view(form_list=(form_pair,))
        response = view(request)

        assert response.template_name == [view_class.templates[step_name]]


@patch.object(views, 'has_company', Mock(return_value=True))
@patch.object(views.SupplierCompanyProfileEditView, 'serialize_form_data',
              Mock(return_value={'field': 'value'}))
@patch.object(views.api_client.company, 'update_profile')
def test_company_profile_edit_api_client_call(
    mock_update_profile, company_request
):
    view = views.SupplierCompanyProfileEditView()
    view.request = company_request
    view.done()
    mock_update_profile.assert_called_once_with(
        sso_user_id=1, data={'field': 'value'}
    )


@patch.object(views, 'has_company', Mock(return_value=True))
@patch.object(views.SupplierCompanyProfileEditView, 'serialize_form_data',
              Mock(return_value={}))
@patch.object(views.api_client.company, 'update_profile')
def test_company_profile_edit_api_client_success(
    mock_update_profile, company_request, api_response_200
):
    mock_update_profile.return_value = api_response_200

    view = views.SupplierCompanyProfileEditView()
    view.request = company_request
    response = view.done()
    assert response.status_code == http.client.FOUND


@patch.object(views, 'has_company', Mock(return_value=True))
@patch.object(views.SupplierCompanyProfileEditView, 'serialize_form_data',
              Mock(return_value={}))
@patch.object(views.api_client.company, 'update_profile')
def test_company_profile_edit_api_client_failure(
    mock_update_profile, company_request, api_response_400
):
    mock_update_profile.return_value = api_response_400

    view = views.SupplierCompanyProfileEditView()
    view.request = company_request
    response = view.done()
    assert response.status_code == http.client.OK
    assert response.template_name == (
        views.SupplierCompanyProfileEditView.failure_template
    )


@patch.object(views, 'has_company', Mock(return_value=True))
@patch.object(views.api_client.company, 'retrieve_profile')
def test_company_profile_edit_calls_api(
    mock_retrieve_profile, company_request, api_response_company_profile_200
):

    mock_retrieve_profile.return_value = api_response_company_profile_200
    view = views.SupplierCompanyProfileEditView.as_view()

    view(company_request)

    assert mock_retrieve_profile.called_once_with(1)


@patch.object(views, 'has_company', Mock(return_value=True))
@patch.object(views.api_client.company, 'retrieve_profile')
def test_company_profile_edit_exposes_api_result_to_form(
    mock_retrieve_profile, company_request, api_response_company_profile_200
):
    mock_retrieve_profile.return_value = api_response_company_profile_200
    view = views.SupplierCompanyProfileEditView.as_view()
    expected = api_response_company_profile_200.json()

    response = view(company_request)

    assert response.context_data['form'].initial == expected


@patch.object(views, 'has_company', Mock(return_value=True))
@patch.object(views.api_client.company, 'retrieve_profile')
def test_company_profile_edit_handles_bad_api_response(
    mock_retrieve_profile, company_request, api_response_400
):
    mock_retrieve_profile.return_value = api_response_400
    view = views.SupplierCompanyProfileEditView.as_view()

    with pytest.raises(requests.exceptions.HTTPError):
        view(company_request)


@patch.object(views, 'has_company', Mock(return_value=False))
def test_supplier_company_redirect_non_verified_company(sso_request):
    view_classes = [
        views.SupplierCompanyProfileEditView,
        views.SupplierCompanyProfileLogoEditView,
        views.SupplierCompanyDescriptionEditView,
    ]
    for ViewClass in view_classes:
        response = ViewClass.as_view()(sso_request)

        assert response.status_code == http.client.FOUND
        assert response.get('Location') == reverse('register-instructions')


@patch.object(views, 'has_company', Mock(return_value=True))
def test_company_edit_views_use_correct_template(client, rf, sso_user):
    request = rf.get(reverse('company-edit'))
    request.sso_user = sso_user
    request.session = client.session
    view_class = views.SupplierCompanyProfileEditView
    assert view_class.form_list
    for form_pair in view_class.form_list:
        step_name = form_pair[0]
        view = view_class.as_view(form_list=(form_pair,))
        response = view(request)

        assert response.template_name == [view_class.templates[step_name]]


@patch.object(views, 'has_company', Mock(return_value=True))
@patch.object(views.SupplierCompanyProfileLogoEditView, 'serialize_form_data',
              Mock(return_value={'field': 'value'}))
@patch.object(views.api_client.company, 'update_profile')
def test_company_profile_logo_api_client_call(mock_update_profile,
                                              company_request):
    view = views.SupplierCompanyProfileLogoEditView()
    view.request = company_request
    view.done()
    mock_update_profile.assert_called_once_with(
        sso_user_id=1, data={'field': 'value'}
    )


@patch.object(views, 'has_company', Mock(return_value=True))
@patch.object(views.SupplierCompanyProfileLogoEditView, 'serialize_form_data',
              Mock(return_value={}))
@patch.object(views.api_client.company, 'update_profile')
def test_company_profile_logo_api_client_success(
    mock_update_profile, company_request, api_response_200
):
    mock_update_profile.return_value = api_response_200

    view = views.SupplierCompanyProfileLogoEditView()
    view.request = company_request
    response = view.done()
    assert response.status_code == http.client.FOUND


@patch.object(views, 'has_company', Mock(return_value=True))
@patch.object(views.SupplierCompanyProfileLogoEditView, 'serialize_form_data',
              Mock(return_value={}))
@patch.object(views.api_client.company, 'update_profile')
def test_company_profile_logo_api_client_failure(
    mock_update_profile, company_request, api_response_400
):
    mock_update_profile.return_value = api_response_400

    view = views.SupplierCompanyProfileLogoEditView()
    view.request = company_request
    response = view.done()
    assert response.status_code == http.client.OK
    expected_template_name = (
        views.SupplierCompanyProfileLogoEditView.failure_template
    )
    assert response.template_name == expected_template_name


@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch('company.forms.CompanyAddressVerificationForm.is_form_tampered',
       Mock(return_value=False))
@patch.object(views, 'has_company', Mock(return_value=True))
@patch.object(views.api_client.company, 'update_profile')
def test_supplier_company_profile_edit_create_api_success(
    mock_update_profile, company_profile_edit_end_to_end, sso_user,
    all_company_profile_data, api_response_200
):
    mock_update_profile.return_value = api_response_200

    response = company_profile_edit_end_to_end()

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == reverse('company-detail')
    mock_update_profile.assert_called_once_with(
        data=all_company_profile_data,
        sso_user_id=sso_user.id,
    )


@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch('company.forms.CompanyAddressVerificationForm.is_form_tampered',
       Mock(return_value=False))
@patch.object(views, 'has_company', Mock(return_value=True))
@patch.object(views.api_client.company, 'update_profile')
def test_supplier_company_profile_edit_create_api_failure(
    mock_create_case_study, company_profile_edit_end_to_end, api_response_400
):
    mock_create_case_study.return_value = api_response_400

    response = company_profile_edit_end_to_end()

    view = views.SupplierCompanyProfileEditView
    assert response.status_code == http.client.OK
    assert response.template_name == view.failure_template


@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch.object(views, 'has_company', Mock(return_value=True))
def test_supplier_company_profile_initial_address_from_profile(
    company_profile_edit_goto_step, retrieve_profile_data
):
    expected = retrieve_profile_data['contact_details'].copy()
    expected['signature'] = Wildcard()

    response = company_profile_edit_goto_step(
        step=views.SupplierCompanyProfileEditView.ADDRESS
    )

    assert response.context_data['form'].initial == expected


@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch.object(views, 'has_company', Mock(return_value=True))
@patch('api_client.api_client.company.retrieve_profile')
def test_supplier_company_profile_initial_address_from_companies_house(
    mock_retrieve_profile, company_profile_edit_goto_step,
    company_profile_companies_house_data,
    api_response_company_profile_no_contact_details
):
    mock_retrieve_profile.return_value = (
        api_response_company_profile_no_contact_details
    )

    expected = company_profile_companies_house_data.copy()
    expected['signature'] = Wildcard()

    response = company_profile_edit_goto_step(
        step=views.SupplierCompanyProfileEditView.ADDRESS
    )
    assert response.context_data['form'].initial == expected


@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch.object(views, 'has_company', Mock(return_value=True))
def test_supplier_company_profile_initial_data_contact_from_profile(
    company_profile_edit_goto_step, retrieve_profile_data
):
    expected = retrieve_profile_data['contact_details']

    response = company_profile_edit_goto_step(
        step=views.SupplierCompanyProfileEditView.CONTACT
    )

    assert response.context_data['form'].initial == expected


@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch.object(views, 'has_company', Mock(return_value=True))
@patch('api_client.api_client.company.retrieve_profile')
def test_supplier_company_profile_initial_contact_from_companies_house(
    mock_retrieve_profile, company_profile_edit_goto_step,
    company_profile_companies_house_data,
    api_response_company_profile_no_contact_details
):
    mock_retrieve_profile.return_value = (
        api_response_company_profile_no_contact_details
    )

    expected = company_profile_companies_house_data

    response = company_profile_edit_goto_step(
        step=views.SupplierCompanyProfileEditView.CONTACT
    )

    assert response.context_data['form'].initial == expected


@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch.object(views, 'has_company', Mock(return_value=True))
def test_supplier_company_profile_initial_data_basic(
    company_profile_edit_goto_step, retrieve_profile_data
):
    response = company_profile_edit_goto_step(
        step=views.SupplierCompanyProfileEditView.BASIC
    )

    assert response.context_data['form'].initial == retrieve_profile_data


@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch.object(views, 'has_company', Mock(return_value=True))
def test_supplier_company_profile_initial_data_classification(
    company_profile_edit_goto_step, retrieve_profile_data
):
    response = company_profile_edit_goto_step(
        step=views.SupplierCompanyProfileEditView.CLASSIFICATION
    )

    assert response.context_data['form'].initial == retrieve_profile_data


@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch('company.forms.CompanyAddressVerificationForm.is_form_tampered',
       Mock(return_value=False))
@patch.object(views, 'has_company', Mock(return_value=True))
@patch.object(validators.api_client.company, 'verify_with_code')
def test_company_address_validation_api_success(
    mock_verify_with_code, address_verification_end_to_end, sso_user,
    all_address_verification_data, api_response_200
):
    mock_verify_with_code.return_value = api_response_200

    response = address_verification_end_to_end()
    assert response.status_code == http.client.FOUND
    assert response.get('Location') == reverse('company-detail')
    mock_verify_with_code.assert_called_with(
        code=all_address_verification_data['code'],
        sso_user_id=sso_user.id,
    )


@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch('company.forms.CompanyAddressVerificationForm.is_form_tampered',
       Mock(return_value=False))
@patch.object(views, 'has_company', Mock(return_value=True))
@patch.object(views.api_client.company, 'verify_with_code')
def test_company_address_validation_api_failure(
    mock_verify_with_code, address_verification_end_to_end, api_response_400
):
    mock_verify_with_code.return_value = api_response_400

    response = address_verification_end_to_end()
    expected = [validators.MESSAGE_INVALID_CODE]

    assert response.status_code == http.client.OK
    assert response.context_data['form'].errors['code'] == expected


@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch.object(views, 'has_company', Mock(return_value=True))
@patch.object(helpers, 'get_contact_details')
def test_supplier_address_edit_standalone_initial_data(
    mock_get_contact_details, client, sso_user,
):
    expected_initial_data = {'field': 'value'}
    mock_get_contact_details.return_value = expected_initial_data

    response = client.get(reverse('company-edit-address'))

    mock_get_contact_details.assert_called_with(sso_user.id)
    assert response.context_data['form'].initial == expected_initial_data


@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch('company.forms.CompanyAddressVerificationForm.is_form_tampered',
       Mock(return_value=False))
@patch.object(views, 'has_company', Mock(return_value=True))
@patch.object(helpers, 'get_contact_details',
              Mock(return_value={}))
@patch.object(views.api_client.company, 'update_profile')
def test_supplier_address_edit_standalone_view_api_success(
    mock_update_profile, client, supplier_address_data_standalone, sso_user,
    api_response_200,
):
    mock_update_profile.return_value = api_response_200

    url = reverse('company-edit-address')
    client.post(url, supplier_address_data_standalone)

    mock_update_profile.assert_called_once_with(
        sso_user_id=sso_user.id,
        data={
            'contact_details': {
                'postal_code': 'E14 6XK',
                'country': 'GB',
                'address_line_2': 'Fakeville',
                'postal_full_name': 'Jeremy',
                'address_line_1': '123 Fake Street',
                'po_box': 'abc',
                'locality': 'London'
            }
        }
    )


@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch.object(views, 'has_company', Mock(return_value=True))
def test_supplier_contact_edit_standalone_initial_data(
    client, retrieve_profile_data
):
    response = client.get(reverse('company-edit-contact'))
    expected = retrieve_profile_data['contact_details']

    assert response.context_data['form'].initial == expected


@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch.object(views, 'has_company', Mock(return_value=True))
@patch.object(views.api_client.company, 'update_profile')
def test_supplier_contact_edit_standalone_view_api_success(
    mock_update_profile, client, company_profile_contact_standalone_data,
    api_response_200, sso_user,
):
    mock_update_profile.return_value = api_response_200

    url = reverse('company-edit-contact')
    client.post(url, company_profile_contact_standalone_data)

    mock_update_profile.assert_called_once_with(
        sso_user_id=sso_user.id,
        data={
            'contact_details': {
                'email_full_name': 'Jeremy',
                'email_address': 'test@example.com',
                'mobile_number': '07555555555'
            }
        }
    )


@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch.object(views, 'has_company', Mock(return_value=True))
def test_supplier_sectors_edit_standalone_initial_data(
    client, retrieve_profile_data
):
    response = client.get(reverse('company-edit-sectors'))

    assert response.context_data['form'].initial == retrieve_profile_data


@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch.object(views, 'has_company', Mock(return_value=True))
@patch.object(views.api_client.company, 'update_profile')
def test_supplier_sectors_edit_standalone_view_api_success(
    mock_update_profile, client, company_profile_sectors_standalone_data,
    api_response_200, sso_user,
):
    mock_update_profile.return_value = api_response_200

    url = reverse('company-edit-sectors')
    client.post(url, company_profile_sectors_standalone_data)

    mock_update_profile.assert_called_once_with(
        sso_user_id=sso_user.id,
        data={
            'sectors': [choices.COMPANY_CLASSIFICATIONS[1][0]]
        }
    )


@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch.object(views, 'has_company', Mock(return_value=True))
def test_supplier_key_facts_edit_standalone_initial_data(
    client, retrieve_profile_data
):
    response = client.get(reverse('company-edit-key-facts'))

    assert response.context_data['form'].initial == retrieve_profile_data


@patch('sso.middleware.SSOUserMiddleware.process_request', process_request)
@patch.object(views, 'has_company', Mock(return_value=True))
@patch.object(views.api_client.company, 'update_profile')
def test_supplier_key_facts_edit_standalone_view_api_success(
    mock_update_profile, client, company_profile_key_facts_standalone_data,
    api_response_200, sso_user,
):
    mock_update_profile.return_value = api_response_200

    url = reverse('company-edit-key-facts')

    client.post(url, company_profile_key_facts_standalone_data)
    mock_update_profile.assert_called_once_with(
        sso_user_id=sso_user.id,
        data={
            'name': 'Example Corp.',
            'website': 'http://www.example.com',
            'keywords': 'Nice, Great',
            'employees': choices.EMPLOYEES[1][0],
        }
    )
