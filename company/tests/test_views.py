import http
from unittest.mock import call, patch, Mock
import urllib

from directory_constants import choices, urls, user_roles
from directory_api_client.client import api_client
import pytest
import requests

from django.core.urlresolvers import reverse

from company import forms, views, validators
from core.tests.helpers import create_response


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
def address_verification_address_data():
    view = views.CompanyAddressVerificationView
    data = {'code': '111111111111'}
    step = view.ADDRESS
    return {
        'company_address_verification_view-current_step': step,
        step + '-code': data['code'],
    }


@pytest.fixture
def address_verification_end_to_end(
    client, user, address_verification_address_data, retrieve_profile_data
):
    user.company = retrieve_profile_data
    client.force_login(user)

    view = views.CompanyAddressVerificationView
    data_step_pairs = [
        [view.ADDRESS, address_verification_address_data],
    ]

    def inner(case_study_id=''):
        url = reverse('verify-company-address-confirm')
        for key, data in data_step_pairs:
            response = client.post(url, data)
        return response
    return inner


@pytest.fixture
def send_verification_letter_end_to_end(
    all_company_profile_data, retrieve_profile_data, client, user
):
    user.company = retrieve_profile_data
    client.force_login(user)

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
            response = client.post(url, data)
        return response
    return inner


def test_send_verification_letter_address_context_data(
    client, user, retrieve_profile_data
):
    retrieve_profile_data['is_verified'] = False
    user.company = retrieve_profile_data
    client.force_login(user)

    response = client.get(reverse('verify-company-address'))

    assert response.context['company_name'] == 'Great company'
    assert response.context['company_number'] == 123456
    assert response.context['company_address'] == (
        '123 Fake Street, Fakeville, London, GB, E14 6XK'
    )


@patch.object(
    api_client.company, 'verify_with_code', return_value=create_response(200)
)
def test_company_address_validation_api_success(
    mock_verify_with_code, address_verification_end_to_end, user,
    settings, retrieve_profile_data
):
    retrieve_profile_data['is_verified'] = False
    view = views.CompanyAddressVerificationView

    response = address_verification_end_to_end()

    assert response.status_code == http.client.OK
    assert response.template_name == view.templates[view.SUCCESS]
    mock_verify_with_code.assert_called_with(
        code='1'*12,
        sso_session_id=user.session_id,
    )


@patch.object(api_client.company, 'verify_with_code')
def test_company_address_validation_api_failure(
    mock_verify_with_code, address_verification_end_to_end,
    retrieve_profile_data
):
    retrieve_profile_data['is_verified'] = False
    mock_verify_with_code.return_value = create_response(400)

    response = address_verification_end_to_end()
    expected = [validators.MESSAGE_INVALID_CODE]

    assert response.status_code == http.client.OK
    assert response.context_data['form'].errors['code'] == expected


def test_unsubscribe_logged_in_user(client, user):
    client.force_login(user)

    response = client.get(reverse('unsubscribe'))

    view = views.EmailUnsubscribeView
    assert response.status_code == http.client.OK
    assert response.template_name == [view.template_name]


def test_unsubscribe_anon_user(client):
    response = client.get(reverse('unsubscribe'))

    assert response.status_code == http.client.FOUND


@patch.object(api_client.supplier, 'unsubscribe')
def test_unsubscribe_api_failure(
    mock_unsubscribe, client, user, retrieve_profile_data
):
    retrieve_profile_data.clear()
    client.force_login(user)
    mock_unsubscribe.return_value = create_response(400)

    with pytest.raises(requests.exceptions.HTTPError):
        client.post(reverse('unsubscribe'))

    mock_unsubscribe.assert_called_once_with(sso_session_id='123')


@patch.object(
    api_client.supplier, 'unsubscribe', return_value=create_response(200)
)
def test_unsubscribe_api_success(
    mock_unsubscribe, client, user, retrieve_profile_data
):
    retrieve_profile_data.clear()
    client.force_login(user)
    response = client.post(reverse('unsubscribe'))

    mock_unsubscribe.assert_called_once_with(sso_session_id='123')
    view = views.EmailUnsubscribeView
    assert response.status_code == http.client.OK
    assert response.template_name == view.success_template


def test_robots(client):
    response = client.get(reverse('robots'))

    assert response.status_code == 200


def test_companies_house_oauth2_has_company_redirects(
    settings, client, user, retrieve_profile_data
):
    retrieve_profile_data['is_verified'] = False

    user.company = retrieve_profile_data
    client.force_login(user)

    url = reverse('verify-companies-house')
    response = client.get(url)

    assert response.status_code == 302

    assert urllib.parse.unquote_plus(response.url) == (
        'https://account.companieshouse.gov.uk/oauth2/authorise'
        '?client_id=debug'
        '&redirect_uri=http://testserver/find-a-buyer/'
        'companies-house-oauth2-callback/'
        '&response_type=code&scope=https://api.companieshouse.gov.uk/'
        'company/123456'
    )


@patch.object(forms.CompaniesHouseClient, 'verify_oauth2_code')
def test_companies_house_callback_missing_code(
    mock_verify_oauth2_code, settings, client, user, retrieve_profile_data
):
    retrieve_profile_data['is_verified'] = False
    user.company = retrieve_profile_data
    client.force_login(user)

    url = reverse('verify-companies-house-callback')  # missing code
    response = client.get(url)

    assert response.status_code == 200
    assert mock_verify_oauth2_code.call_count == 0


@patch.object(forms.CompaniesHouseClient, 'verify_oauth2_code')
@patch.object(
    api_client.company, 'verify_with_companies_house',
    return_value=create_response(200)
)
def test_companies_house_callback_has_company_calls_companies_house(
    mock_verify_with_companies_house, mock_verify_oauth2_code, settings,
    client, user, retrieve_profile_data
):
    retrieve_profile_data['is_verified'] = False
    user.company = retrieve_profile_data
    client.force_login(user)

    mock_verify_oauth2_code.return_value = create_response(
        status_code=200, json_body={'access_token': 'abc'}
    )

    url = reverse('verify-companies-house-callback')
    response = client.get(url, {'code': '111111111111'})

    assert response.status_code == 302
    assert response.url == str(
        views.CompaniesHouseOauth2CallbackView.success_url
    )

    assert mock_verify_oauth2_code.call_count == 1
    assert mock_verify_oauth2_code.call_args == call(
        code='111111111111',
        redirect_uri=(
            'http://testserver/find-a-buyer/companies-house-oauth2-callback/'
        )
    )

    assert mock_verify_with_companies_house.call_count == 1
    assert mock_verify_with_companies_house.call_args == call(
        sso_session_id=user.session_id,
        access_token='abc',
    )


@patch.object(forms.CompaniesHouseClient, 'verify_oauth2_code')
@patch.object(
    api_client.company, 'verify_with_companies_house',
    return_value=create_response(200)
)
def test_companies_house_callback_has_company_calls_url_prefix(
    mock_verify_with_companies_house, mock_verify_oauth2_code, settings,
    client, user, retrieve_profile_data
):
    retrieve_profile_data['is_verified'] = False
    user.company = retrieve_profile_data
    client.force_login(user)
    mock_verify_oauth2_code.return_value = create_response(
        status_code=200, json_body={'access_token': 'abc'}
    )

    url = reverse('verify-companies-house-callback')
    response = client.get(url, {'code': '111111111111'})

    assert response.status_code == 302
    assert response.url == str(
        views.CompaniesHouseOauth2CallbackView.success_url
    )

    assert mock_verify_oauth2_code.call_count == 1
    assert mock_verify_oauth2_code.call_args == call(
        code='111111111111',
        redirect_uri=(
            'http://testserver/find-a-buyer/companies-house-oauth2-callback/'
        )
    )


@patch.object(forms.CompaniesHouseClient, 'verify_oauth2_code')
@patch.object(
    api_client.company, 'verify_with_companies_house',
    return_value=create_response(500)
)
def test_companies_house_callback_error(
    mock_verify_with_companies_house, mock_verify_oauth2_code, settings,
    client, user, retrieve_profile_data
):
    retrieve_profile_data['is_verified'] = False
    user.company = retrieve_profile_data
    client.force_login(user)

    mock_verify_oauth2_code.return_value = create_response(
        status_code=200, json_body={'access_token': 'abc'}
    )

    url = reverse('verify-companies-house-callback')
    response = client.get(url, {'code': '111111111111'})

    assert response.status_code == 200
    assert response.template_name == (
        views.CompaniesHouseOauth2CallbackView.error_template
    )


@patch.object(forms.CompaniesHouseClient, 'verify_oauth2_code')
def test_companies_house_callback_invalid_code(
    mock_verify_oauth2_code, settings, client, user, retrieve_profile_data
):
    retrieve_profile_data['is_verified'] = False
    user.company = retrieve_profile_data
    client.force_login(user)

    mock_verify_oauth2_code.return_value = create_response(400)

    url = reverse('verify-companies-house-callback')
    response = client.get(url, {'code': '111111111111'})

    assert response.status_code == 200
    assert b'Invalid code.' in response.content


@patch.object(forms.CompaniesHouseClient, 'verify_oauth2_code')
def test_companies_house_callback_unauthorized(
    mock_verify_oauth2_code, settings, client, user, retrieve_profile_data
):
    retrieve_profile_data['is_verified'] = False
    user.company = retrieve_profile_data
    client.force_login(user)

    mock_verify_oauth2_code.return_value = create_response(401)

    url = reverse('verify-companies-house-callback')
    response = client.get(url, {'code': '111111111111'})

    assert response.status_code == 200
    assert b'Invalid code.' in response.content


def test_verify_company_has_company_user(
    settings, client, user, retrieve_profile_data
):
    retrieve_profile_data['is_verified'] = False
    user.company = retrieve_profile_data
    client.force_login(user)

    url = reverse('verify-company-hub')
    response = client.get(url)

    assert response.status_code == 200
    assert response.template_name == [views.CompanyVerifyView.template_name]


def test_verify_company_address_feature_flag_on(
    settings, client, user, retrieve_profile_data
):
    retrieve_profile_data['is_verified'] = False
    user.company = retrieve_profile_data
    client.force_login(user)

    response = client.get(reverse('verify-company-address'))

    assert response.status_code == 200


@patch.object(api_client.company, 'profile_update')
def test_verify_company_address_end_to_end(
    mock_profile_update, settings, send_verification_letter_end_to_end,
    retrieve_profile_data
):
    retrieve_profile_data['is_verified'] = False
    mock_profile_update.return_value = create_response(200)
    view = views.SendVerificationLetterView

    response = send_verification_letter_end_to_end()

    assert response.status_code == 200
    assert response.template_name == view.templates[view.SENT]
    assert response.context_data['profile_url'] == 'http://profile.trade.great:8006/profile/business-profile/'
    assert mock_profile_update.call_count == 1
    assert mock_profile_update.call_args == call(
        data={'postal_full_name': 'Jeremy'},
        sso_session_id='123'
    )


multi_user_urls = [
    reverse('add-collaborator'),
    reverse('remove-collaborator'),
    reverse('account-transfer'),
]


@pytest.mark.parametrize('url', multi_user_urls)
@patch.object(api_client.company, 'collaborator_list')
def test_multi_user_view_has_company(
    mock_collaborator_list, url, client, user, retrieve_profile_data,
):
    user.company = retrieve_profile_data
    client.force_login(user)
    mock_collaborator_list.return_value = create_response(
        json_body=[{'sso_id': 1, 'company_email': 'test@example.com'}]
    )

    response = client.get(url)

    assert response.status_code == 200


@patch.object(api_client.company, 'collaborator_invite_create')
def test_add_collaborator_invalid_form(
    mock_collaborator_invite_create, client, user, retrieve_profile_data, retrieve_supplier_profile_data
):
    user.company = retrieve_profile_data
    client.force_login(user)

    url = reverse('add-collaborator')

    response = client.post(url, {})

    assert response.status_code == 200
    assert response.context_data['form'].is_valid() is False
    assert 'email_address' in response.context_data['form'].errors

    assert mock_collaborator_invite_create.call_count == 0


@patch.object(api_client.company, 'collaborator_invite_create', return_value=create_response(200))
def test_add_collaborator_valid_form(
    mock_collaborator_invite_create, client, user, retrieve_profile_data, retrieve_supplier_profile_data
):
    user.company = retrieve_profile_data
    client.force_login(user)

    url = reverse('add-collaborator')

    response = client.post(url, {'email_address': 'a@b.com'})

    assert response.status_code == 302
    assert response.url == (
        'http://profile.trade.great:8006/find-a-buyer/?user-added'
    )

    assert mock_collaborator_invite_create.call_count == 1
    assert mock_collaborator_invite_create.call_args == call(
        sso_session_id=user.session_id,
        collaborator_email='a@b.com',
        role=user_roles.EDITOR,
    )


def test_add_collaborator_email(client, user):
    client.force_login(user)

    url = reverse('add-collaborator')
    response = client.get(url+'?email=test@test1.com')

    assert response.context['form'].initial == {
        'email_address': 'test@test1.com'
    }


def test_add_collaborator_empty_email(client, user):
    client.force_login(user)
    url = reverse('add-collaborator')
    response = client.get(url)

    assert response.status_code == 200
    assert response.context['form'].initial == {
        'email_address': None
    }


@patch.object(api_client.company, 'collaborator_invite_create')
def test_add_collaborator_valid_form_already_exists(
    mock_collaborator_invite_create, client, user,
    retrieve_supplier_profile_data,
):
    client.force_login(user)
    retrieve_supplier_profile_data['is_company_owner'] = True
    mock_collaborator_invite_create.return_value = create_response(400, {'collaborator_email': ['Already exists']})
    url = reverse('add-collaborator')

    response = client.post(url, {'email_address': 'a@b.com'})

    assert response.status_code == 302
    assert response.get('Location') == 'http://profile.trade.great:8006/find-a-buyer/?user-added'


@pytest.mark.parametrize('url,data,mock_path', (
    (
        reverse('add-collaborator'),
        {'email_address': 'a@b.com'},
        'company.views.api_client.company.collaborator_invite_create',
    ),
    (
        reverse('remove-collaborator'),
        {'sso_ids': ['1']},
        'company.views.api_client.company.collaborator_disconnect',
    )
))
@patch.object(api_client.company, 'collaborator_list')
def test_add_collaborator_valid_form_api_error(
    mock_collaborator_list, url, data, mock_path, client, user,
    retrieve_profile_data, retrieve_supplier_profile_data
):
    user.company = retrieve_profile_data
    client.force_login(user)
    mock_collaborator_list.return_value = create_response(
        json_body=[{'sso_id': 1, 'company_email': 'test@example.com'}]
    )

    with patch(mock_path, return_value=create_response(400)):
        with pytest.raises(requests.exceptions.HTTPError):
            client.post(url, data)


@patch.object(api_client.company, 'collaborator_list')
@patch.object(api_client.company, 'collaborator_disconnect')
def test_collaborator_disconnect_invalid_form(
    mock_collaborator_disconnect, mock_collaborator_list,
    client, user, retrieve_profile_data,
    retrieve_supplier_profile_data
):
    user.company = retrieve_profile_data
    client.force_login(user)
    mock_collaborator_list.return_value = create_response(
        json_body=[{'sso_id': 1, 'company_email': 'test@example.com'}]
    )

    url = reverse('remove-collaborator')

    response = client.post(url, {})

    assert response.status_code == 200
    assert response.context_data['form'].is_valid() is False
    assert 'sso_ids' in response.context_data['form'].errors

    assert mock_collaborator_disconnect.call_count == 0


@patch.object(api_client.company, 'collaborator_list')
@patch.object(api_client.company, 'collaborator_disconnect', return_value=create_response(200))
def test_collaborator_disconnect_valid_form(
    mock_collaborator_disconnect, mock_collaborator_list,
    client, user, retrieve_profile_data, retrieve_supplier_profile_data
):
    user.company = retrieve_profile_data
    client.force_login(user)
    mock_collaborator_list.return_value = create_response(
        json_body=[{'sso_id': 1, 'company_email': 'test@example.com'}]
    )

    url = reverse('remove-collaborator')

    response = client.post(url, {'sso_ids': ['1']})

    assert response.status_code == 302
    assert response.url == (
        'http://profile.trade.great:8006/find-a-buyer/?user-removed'
    )

    assert mock_collaborator_disconnect.call_count == 1
    assert mock_collaborator_disconnect.call_args == call(sso_session_id=user.session_id, sso_id='1')


@patch.object(api_client.company, 'collaborator_invite_create')
def test_transfer_owner_invalid_form(
    ock_collaborator_invite_create, client, user, retrieve_profile_data
):
    user.company = retrieve_profile_data
    client.force_login(user)

    view = views.TransferAccountWizardView

    response = client.post(
        reverse('account-transfer'),
        {
            'transfer_account_wizard_view-current_step': view.EMAIL,
            view.EMAIL + '-email_address': 'a.com'
        }
    )

    assert response.status_code == 200
    assert response.context_data['form'].is_valid() is False
    assert 'email_address' in response.context_data['form'].errors

    assert ock_collaborator_invite_create.call_count == 0


def test_company_address_verification_backwards_compatible_feature_flag_on(
    settings, client
):
    url = reverse('verify-company-address-historic-url')
    response = client.get(url)

    assert response.status_code == 302
    assert response.get('Location') == reverse('verify-company-address')


@patch.object(api_client.company, 'collaborator_invite_create')
@patch.object(forms.sso_api_client.user, 'check_password')
def test_transfer_owner_invalid_password(
    mock_check_password, mock_collaborator_invite_create, client, user,
    retrieve_profile_data, retrieve_supplier_profile_data
):

    user.company = retrieve_profile_data
    client.force_login(user)

    mock_check_password.return_value = create_response(400)

    view = views.TransferAccountWizardView

    client.post(
        reverse('account-transfer'),
        {
            'transfer_account_wizard_view-current_step': view.EMAIL,
            view.EMAIL + '-email_address': 'a@b.com'
        }
    )
    response = client.post(
        reverse('account-transfer'),
        {
            'transfer_account_wizard_view-current_step': view.PASSWORD,
            view.PASSWORD + '-password': 'password'
        }
    )

    expected_error = forms.TransferAccountPasswordForm.MESSAGE_INVALID_PASSWORD
    assert response.status_code == 200
    assert response.context_data['form'].errors['password'] == [expected_error]

    assert mock_collaborator_invite_create.call_count == 0


@patch.object(api_client.company, 'collaborator_invite_create')
@patch(
    'company.forms.sso_api_client.user.check_password',
    Mock(return_value=create_response(200))
)
def test_transfer_owner_valid_form(
    mock_collaborator_invite_create, client, user, retrieve_profile_data,
    retrieve_supplier_profile_data
):
    user.company = retrieve_profile_data
    client.force_login(user)

    view = views.TransferAccountWizardView

    client.post(
        reverse('account-transfer'),
        {
            'transfer_account_wizard_view-current_step': view.EMAIL,
            view.EMAIL + '-email_address': 'a@b.com'
        }
    )
    response = client.post(
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
    assert mock_collaborator_invite_create.call_count == 1
    assert mock_collaborator_invite_create.call_args == call(
        sso_session_id=user.session_id,
        collaborator_email='a@b.com',
        role=user_roles.ADMIN,
    )


@patch.object(api_client.company, 'collaborator_invite_create')
@patch.object(forms.sso_api_client.user, 'check_password')
def test_transfer_owner_valid_form_already_exists(
    mock_check_password, mock_collaborator_invite_create, client, user,
    retrieve_profile_data, retrieve_supplier_profile_data
):
    user.company = retrieve_profile_data
    client.force_login(user)

    mock_check_password.return_value = mock_collaborator_invite_create
    mock_collaborator_invite_create.return_value = create_response(
        http.client.BAD_REQUEST, {'collaborator_email': ['Already exists']}
    )

    view = views.TransferAccountWizardView

    client.post(
        reverse('account-transfer'),
        {
            'transfer_account_wizard_view-current_step': view.EMAIL,
            view.EMAIL + '-email_address': 'a@b.com'
        }
    )
    response = client.post(
        reverse('account-transfer'),
        {
            'transfer_account_wizard_view-current_step': view.PASSWORD,
            view.PASSWORD + '-password': 'password'
        }
    )

    assert response.status_code == 302
    assert response.url == 'http://profile.trade.great:8006/find-a-buyer/?owner-transferred'


@patch.object(api_client.company, 'collaborator_invite_create')
@patch(
    'company.forms.sso_api_client.user.check_password',
    return_value=create_response(200)
)
def test_transfer_owner_valid_form_api_error(
    mock_check_password, mock_collaborator_invite_create, client, user,
    retrieve_profile_data, retrieve_supplier_profile_data
):
    user.company = retrieve_profile_data
    client.force_login(user)

    mock_collaborator_invite_create.return_value = create_response(400)

    view = views.TransferAccountWizardView
    url = reverse('account-transfer')

    client.post(
        reverse('account-transfer'),
        {
            'transfer_account_wizard_view-current_step': view.EMAIL,
            view.EMAIL + '-email_address': 'a@b.com'
        }
    )
    with pytest.raises(requests.exceptions.HTTPError):
        client.post(
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


@patch('directory_api_client.api_client.company.collaborator_invite_retrieve')
def test_accept_ownership_invite_get_invite_no_supplier(
    mock_retrieve_api_method, client, user, retrieve_supplier_profile_data, retrieve_profile_data
):
    mock_retrieve_api_method.return_value = create_response(json_body={'company_name': 'name'})
    retrieve_supplier_profile_data.clear()
    client.force_login(user)

    url = reverse('account-transfer-accept')
    response = client.get(url)

    assert response.status_code == 200


def test_add_collaborator_invite_get_invite_no_supplier(
    client, user, retrieve_supplier_profile_data, retrieve_profile_data
):
    retrieve_supplier_profile_data.clear()
    client.force_login(user)

    url = reverse('add-collaborator')
    response = client.get(url)

    assert response.status_code == 302
    assert response.url.startswith(urls.domestic.FIND_A_BUYER)


@patch('directory_api_client.api_client.company.collaborator_invite_retrieve')
def test_accept_ownership_invite_get_invite(
    mock_retrieve_api_method, client, user, retrieve_supplier_profile_data,
    retrieve_profile_data
):
    retrieve_supplier_profile_data['is_company_owner'] = False
    client.force_login(user)
    mock_retrieve_api_method.return_value = create_response(
        json_body={'company_name': 'name'}
    )

    url = reverse('account-transfer-accept')
    response = client.get(url)

    assert response.status_code == 200
    assert response.context_data['invite'] == {'company_name': 'name'}


@patch('directory_api_client.api_client.company.collaborator_invite_retrieve')
def test_accept_collaborate_invite_get_invite(
    mock_retrieve_api_method, client, user, retrieve_profile_data
):
    retrieve_profile_data.clear()
    client.force_login(user)
    mock_retrieve_api_method.return_value = create_response(
        json_body={'company_name': 'name'}
    )

    url = reverse('account-collaborate-accept')
    response = client.get(url)

    assert response.status_code == 200
    assert response.context_data['invite'] == {'company_name': 'name'}


@patch('directory_api_client.api_client.company.collaborator_invite_retrieve')
def test_accept_ownership_invite_no_invite_key(
    mock_retrieve_api_method, client, user, retrieve_supplier_profile_data
):
    retrieve_supplier_profile_data['is_company_owner'] = False
    client.force_login(user)
    mock_retrieve_api_method.return_value = create_response(
        json_body={'company_name': 'name'}
    )

    url = reverse('account-transfer-accept')
    response = client.post(url, data={})

    assert response.status_code == 200
    assert response.context_data['form'].is_valid() is False
    assert 'invite_key' in response.context_data['form'].errors


@patch('directory_api_client.api_client.company.collaborator_invite_retrieve')
def test_accept_collaborate_invite_no_invite_key(
    mock_retrieve_api_method, client, user, retrieve_profile_data
):
    retrieve_profile_data.clear()
    mock_retrieve_api_method.return_value = create_response(
        json_body={'company_name': 'name'}
    )
    client.force_login(user)

    url = reverse('account-collaborate-accept')
    response = client.post(url, data={})

    assert response.status_code == 200
    assert response.context_data['form'].is_valid() is False
    assert 'invite_key' in response.context_data['form'].errors


@patch('directory_api_client.api_client.company.collaborator_invite_retrieve')
@patch(
    'directory_api_client.api_client.company.collaborator_invite_accept', Mock(return_value=create_response(200))
)
def test_accept_ownership_invite_valid_invite_key(
    mock_retrieve_api_method, client, user, retrieve_supplier_profile_data
):
    retrieve_supplier_profile_data['is_company_owner'] = False
    client.force_login(user)
    mock_retrieve_api_method.return_value = create_response(
        json_body={'company_name': 'name'}
    )
    url = reverse('account-transfer-accept')

    response = client.post(url, data={'invite_key': '123'})

    assert response.status_code == 302
    assert response.url == urls.domestic.FIND_A_BUYER


@patch('directory_api_client.api_client.company.collaborator_invite_retrieve')
@patch(
    'directory_api_client.api_client.company.collaborator_invite_accept', Mock(return_value=create_response(200))
)
def test_accept_collaborate_invite_valid_invite_key(
    mock_retrieve_api_method, client, user,
    retrieve_profile_data
):
    retrieve_profile_data.clear()
    client.force_login(user)
    mock_retrieve_api_method.return_value = create_response(
        json_body={'company_name': 'name'}
    )

    url = reverse('account-collaborate-accept')

    response = client.post(url, data={'invite_key': '123'})

    assert response.status_code == 302
    assert response.url == urls.domestic.FIND_A_BUYER


@patch('directory_api_client.api_client.company.collaborator_invite_retrieve')
def test_accept_invite_transfer_invite_key_invalid(
    mock_retrieve_api_method, client, user, retrieve_profile_data,
    retrieve_supplier_profile_data
):
    retrieve_supplier_profile_data['is_company_owner'] = False
    user.company = retrieve_profile_data
    client.force_login(user)

    mock_retrieve_api_method.return_value = create_response(400)
    url = reverse('account-transfer-accept')

    response = client.get(url)

    assert response.status_code == 200
    assert response.context_data['invite'] is None


@patch('directory_api_client.api_client.company.collaborator_invite_retrieve')
def test_accept_invite_collaborate_invitekey_invalid(
    mock_retrieve_api_method, client, user, retrieve_profile_data
):
    retrieve_profile_data.clear()
    client.force_login(user)
    mock_retrieve_api_method.return_value = create_response(400)

    url = reverse('account-collaborate-accept')

    response = client.get(url)

    assert response.status_code == 200
    assert response.context_data['invite'] is None


def test_case_study_create_backwards_compatible_url(client):
    url = reverse('company-case-study-create-backwards-compatible')
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == urls.domestic.SINGLE_SIGN_ON_PROFILE


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
