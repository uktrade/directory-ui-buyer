import http
from unittest import mock

import pytest

from django.core.urlresolvers import reverse

from enrolment.constants import SESSION_KEY_REFERRER
from enrolment.views import (
    CompanyProfileDetailView,
    CompanyProfileEditView,
    EmailConfirmationView,
    EnrolmentView,
    api_client,
)
from enrolment import forms


def test_email_confirm_missing_confirmation_code(rf):
    view = EmailConfirmationView.as_view()
    request = rf.get(reverse('confirm-email'))
    response = view(request)
    assert response.status_code == http.client.OK
    assert response.template_name == EmailConfirmationView.failure_template


@mock.patch.object(api_client.registration, 'confirm_email',
                   return_value=False)
def test_email_confirm_invalid_confirmation_code(mock_confirm_email, rf):
    view = EmailConfirmationView.as_view()
    request = rf.get(reverse('confirm-email'), {'confirmation_code': 123})
    response = view(request)
    assert mock_confirm_email.called_with(123)
    assert response.status_code == http.client.OK
    assert response.template_name == EmailConfirmationView.failure_template


@mock.patch.object(api_client.registration, 'confirm_email', return_value=True)
def test_email_confirm_valid_confirmation_code(mock_confirm_email, rf):
    view = EmailConfirmationView.as_view()
    request = rf.get(reverse('confirm-email'), {'confirmation_code': 123})
    response = view(request)
    assert mock_confirm_email.called_with(123)
    assert response.status_code == http.client.OK
    assert response.template_name == EmailConfirmationView.success_template


def test_enrolment_view_includes_referrer(client, rf):
    request = rf.get(reverse('register'))
    request.session = client.session
    request.session[SESSION_KEY_REFERRER] = 'google'

    form_pair = EnrolmentView.form_list[2]
    view = EnrolmentView.as_view(form_list=(form_pair,))
    response = view(request)

    initial = response.context_data['form'].initial
    assert form_pair[0] == 'user'
    assert initial['referrer'] == 'google'


def test_enrolment_view_uses_correct_template(client, rf):
    request = rf.get(reverse('register'))
    request.session = client.session

    for form_pair in EnrolmentView.form_list:
        step_name = form_pair[0]
        view = EnrolmentView.as_view(form_list=(form_pair,))
        response = view(request)

        assert response.template_name == [EnrolmentView.templates[step_name]]


@mock.patch.object(EnrolmentView, 'get_all_cleaned_data', return_value={})
@mock.patch.object(forms, 'serialize_enrolment_forms')
@mock.patch.object(api_client.registration, 'send_form')
def test_enrolment_form_complete_api_client_call(
    mock_send_form, mock_serialize_enrolment_forms, rf, client
):
    view = EnrolmentView()
    view.request = None
    mock_serialize_enrolment_forms.return_value = data = {'field': 'value'}
    view.done()
    mock_send_form.assert_called_once_with(data)


@mock.patch.object(EnrolmentView, 'get_all_cleaned_data', lambda x: {})
@mock.patch.object(forms, 'serialize_enrolment_forms', lambda x: {})
@mock.patch.object(api_client.registration, 'send_form')
def test_enrolment_form_complete_api_client_success(mock_send_form):
    mock_send_form.return_value = mock.Mock(status_code=http.client.OK)
    view = EnrolmentView()
    view.request = None
    response = view.done()
    assert response.template_name == EnrolmentView.success_template


@mock.patch.object(EnrolmentView, 'get_all_cleaned_data', lambda x: {})
@mock.patch.object(forms, 'serialize_enrolment_forms', lambda x: {})
@mock.patch.object(api_client.registration, 'send_form')
def test_enrolment_form_complete_api_client_failure(mock_send_form):
    mock_send_form.return_value = mock.Mock(
        status_code=http.client.BAD_REQUEST
    )
    view = EnrolmentView()
    view.request = None
    response = view.done()
    assert response.template_name == EnrolmentView.failure_template


@mock.patch.object(
    CompanyProfileEditView, 'get_all_cleaned_data', return_value={}
)
@mock.patch.object(forms, 'serialize_company_profile_forms')
@mock.patch.object(api_client.company, 'update_profile')
def test_company_profile_edit_api_client_call(
        mock_update_profile, mock_serialize_company_profile_forms, rf, client):
    view = CompanyProfileEditView()
    view.request = None
    mock_serialize_company_profile_forms.return_value = data = {
        'field': 'value'
    }
    view.done()
    mock_update_profile.assert_called_once_with(data)


@mock.patch.object(
    CompanyProfileEditView, 'get_all_cleaned_data', lambda x: {}
)
@mock.patch.object(forms, 'serialize_company_profile_forms', lambda x: {})
@mock.patch.object(api_client.company, 'update_profile')
def test_company_profile_edit_api_client_success(mock_update_profile):
    mock_update_profile.return_value = mock.Mock(status_code=http.client.OK)
    view = CompanyProfileEditView()
    view.request = None
    response = view.done()
    assert response.status_code == http.client.FOUND


@mock.patch.object(
    CompanyProfileEditView, 'get_all_cleaned_data', lambda x: {}
)
@mock.patch.object(forms, 'serialize_company_profile_forms', lambda x: {})
@mock.patch.object(api_client.company, 'update_profile')
def test_company_profile_edit_api_client_failure(mock_update_profile):
    mock_update_profile.return_value = mock.Mock(
        status_code=http.client.BAD_REQUEST
    )
    view = CompanyProfileEditView()
    view.request = None
    response = view.done()
    assert response.status_code == http.client.OK
    assert response.template_name == CompanyProfileEditView.failure_template


@mock.patch.object(api_client.company, 'retrieve_profile')
def test_company_profile_details_calls_api(
    mock_retrieve_profile, rf, client
):
    view = CompanyProfileDetailView.as_view()
    request = rf.get(reverse('company-detail'))
    request.user = mock.Mock(session=client.session)
    request.user.session['company_id'] = 1

    view(request)

    assert mock_retrieve_profile.called_once_with(1)


@mock.patch.object(api_client.company, 'retrieve_profile')
def test_company_profile_details_exposes_context(
    mock_retrieve_profile, client, rf
):
    mock_retrieve_profile.return_value = expected_context = {
        'website': 'http://example.com',
        'description': 'Ecommerce website',
        'number': 123456,
        'aims': ['Increase Revenue'],
        'logo': ('nice.jpg'),
    }
    view = CompanyProfileDetailView.as_view()
    request = rf.get(reverse('company-detail'))
    # todo: replace mock with something better once login has been stabalised.
    request.user = mock.Mock(session=client.session)
    request.user.session['company_id'] = 1
    response = view(request)
    assert response.status_code == http.client.OK
    assert response.template_name == [CompanyProfileDetailView.template_name]
    assert response.context_data['company'] == expected_context


def test_company_profile_details_logs_missing_session_company(
    client, rf, caplog
):
    view = CompanyProfileDetailView.as_view()
    request = rf.get(reverse('company-detail'))
    request.session = client.session
    # todo: replace mock with something better once login has been stabalised.
    request.user = mock.Mock(session=client.session, id=2)
    with pytest.raises(KeyError):
        response = view(request)
        assert response.status_code == http.client.INTERNAL_SERVER_ERROR
    log = caplog.records[0]
    assert log.message == 'company_id is missing from the user session.'
    assert log.user_id == 2
    assert log.levelname == 'ERROR'


def test_company_profile_edit_view_uses_correct_template(client, rf):
    request = rf.get(reverse('company-edit'))
    request.session = client.session

    for form_pair in CompanyProfileEditView.form_list:
        step_name = form_pair[0]
        view = CompanyProfileEditView.as_view(form_list=(form_pair,))
        response = view(request)

        expected_template_name = CompanyProfileEditView.templates[step_name]
        assert response.template_name == [expected_template_name]
