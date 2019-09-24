from directory_constants import urls, user_roles
from directory_api_client.client import api_client
from formtools.wizard.views import SessionWizardView
from raven.contrib.django.raven_compat.models import client as sentry_client
from requests.exceptions import HTTPError

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.functional import cached_property
from django.views.generic import RedirectView, TemplateView, View
from django.views.generic.edit import FormView
from django.urls import reverse

from company import forms, helpers
from enrolment.helpers import CompaniesHouseClient


class SubmitFormOnGetMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['data'] = self.request.GET or None
        return kwargs

    def get(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UpdateCompanyProfileOnFormWizardDoneMixin:
    def serialize_form_data(self):
        return self.form_serializer(self.get_all_cleaned_data())

    def handle_profile_update_success(self):
        return redirect('company-detail')

    @staticmethod
    def send_update_error_to_sentry(sso_user, api_response):
        # This is needed to not include POST data (e.g. binary image), which
        # was causing sentry to fail at sending
        sentry_client.context.clear()
        sentry_client.user_context(
            {'sso_id': sso_user.id, 'sso_user_email': sso_user.email}
        )
        sentry_client.captureMessage(
            message='Updating company profile failed',
            data={},
            extra={'api_response': str(api_response.content)}
        )

    def done(self, *args, **kwargs):
        response = api_client.company.profile_update(
            sso_session_id=self.request.user.session_id,
            data=self.serialize_form_data()
        )
        try:
            response.raise_for_status()
        except HTTPError:
            self.send_update_error_to_sentry(
                sso_user=self.request.user,
                api_response=response
            )
            raise
        else:
            return self.handle_profile_update_success()


class GetTemplateForCurrentStepMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.templates

    def get_template_names(self):
        return [self.templates[self.steps.current]]


class SendVerificationLetterView(
    GetTemplateForCurrentStepMixin,
    UpdateCompanyProfileOnFormWizardDoneMixin,
    SessionWizardView
):

    ADDRESS = 'address'
    SENT = 'sent'

    form_list = (
        (ADDRESS, forms.CompanyAddressVerificationForm),
    )
    templates = {
        ADDRESS: 'company-profile-form-address.html',
        SENT: 'company-profile-form-letter-sent.html',
    }
    form_labels = [
        (ADDRESS, 'Address'),
    ]
    form_serializer = staticmethod(forms.serialize_company_address_form)

    def get_context_data(self, form, **kwargs):
        address = helpers.build_company_address(self.request.user.company)
        return super().get_context_data(
            form=form,
            form_labels=self.form_labels,
            all_cleaned_data=self.get_all_cleaned_data(),
            company_name=self.request.user.company['name'],
            company_number=self.request.user.company['number'],
            company_address=address,
            **kwargs
        )

    def handle_profile_update_success(self):
        return TemplateResponse(self.request, self.templates[self.SENT])


class CompanyVerifyView(TemplateView):

    template_name = 'company-verify-hub.html'

    def get_context_data(self, **kwargs):
        return {
            'company': self.request.user.company,
        }


class CompanyAddressVerificationView(
    GetTemplateForCurrentStepMixin,
    SessionWizardView
):

    ADDRESS = 'address'
    SUCCESS = 'success'

    form_list = (
        (ADDRESS, forms.CompanyCodeVerificationForm),
    )
    templates = {
        ADDRESS: 'company-profile-address-verification-form.html',
        SUCCESS: 'company-profile-address-verification-success.html'
    }

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)
        kwargs['sso_session_id'] = self.request.user.session_id
        return kwargs

    def done(self, *args, **kwargs):
        return TemplateResponse(
            self.request,
            self.templates[self.SUCCESS]
        )

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            company=self.request.user.company,
            **kwargs
        )


class CompanyAddressVerificationHistoricView(RedirectView):
    pattern_name = 'verify-company-address'


class EmailUnsubscribeView(FormView):

    form_class = forms.EmptyForm
    template_name = 'email-unsubscribe.html'
    success_template = 'email-unsubscribe-success.html'

    def form_valid(self, form):
        response = api_client.supplier.unsubscribe(
            sso_session_id=self.request.user.session_id
        )
        response.raise_for_status()
        return TemplateResponse(self.request, self.success_template)


class RequestPaylodTooLargeErrorView(TemplateView):
    template_name = 'image-too-large.html'

    def dispatch(self, request, *args, **kwargs):
        # the template has a "click here to go back to the form". We get the
        # url from the referer header.
        if 'HTTP_REFERER' not in request.META:
            return redirect('index')
        return super().dispatch(request, *args, **kwargs)


class Oauth2CallbackUrlMixin:
    @property
    def redirect_uri(self):
        return self.request.build_absolute_uri(
            reverse('verify-companies-house-callback')
        )


class CompaniesHouseOauth2View(Oauth2CallbackUrlMixin, RedirectView):

    def get_redirect_url(self):
        company = helpers.get_company_profile(self.request.user.session_id)
        return CompaniesHouseClient.make_oauth2_url(
            company_number=company['number'],
            redirect_uri=self.redirect_uri,
        )


class CompaniesHouseOauth2CallbackView(
    SubmitFormOnGetMixin,
    Oauth2CallbackUrlMixin,
    FormView
):

    form_class = forms.CompaniesHouseOauth2Form
    template_name = 'companies-house-oauth2-callback.html'
    error_template = 'companies-house-oauth2-error.html'
    success_url = urls.domestic.FIND_A_BUYER

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['redirect_uri'] = self.redirect_uri
        return kwargs

    def form_valid(self, form):
        response = api_client.company.verify_with_companies_house(
            sso_session_id=self.request.user.session_id,
            access_token=form.oauth2_response.json()['access_token']
        )
        if response.status_code == 500:
            return TemplateResponse(self.request, self.error_template)
        else:
            return super().form_valid(form)


class BaseMultiUserAccountManagementView:

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs, company_profile_url=settings.SSO_PROFILE_URL
        )


class AddCollaboratorView(BaseMultiUserAccountManagementView, FormView):
    form_class = forms.AddCollaboratorForm
    template_name = 'company-add-collaborator.html'

    def get_form_kwargs(self):
        return {
            **super().get_form_kwargs(),
            'sso_email_address': self.request.user.email
        }

    def get_initial(self):
        initial = super().get_initial()
        initial["email_address"] = self.request.GET.get('email')
        return initial

    def form_valid(self, form):
        self.add_collaborator(email_address=form.cleaned_data['email_address'])
        return super().form_valid(form)

    def add_collaborator(self, email_address):
        response = api_client.company.collaborator_invite_create(
            sso_session_id=self.request.user.session_id,
            collaborator_email=email_address,
            role=user_roles.EDITOR,
        )
        if response.status_code == 400:
            if 'collaborator_email' in response.json():
                # email already has a collaboration invite, but do not tell
                # the user to avoid leaking information to bad actors.
                return
        response.raise_for_status()

    def get_success_url(self):
        return settings.SSO_PROFILE_URL + '?user-added'


class RemoveCollaboratorView(BaseMultiUserAccountManagementView, FormView):
    form_class = forms.RemoveCollaboratorForm
    template_name = 'company-remove-collaborator.html'

    def get_form_kwargs(self, *args, **kwargs):
        form_kwargs = super().get_form_kwargs(*args, **kwargs)
        return {
            'sso_session_id': self.request.user.session_id,
            **form_kwargs
        }

    def form_valid(self, form):
        sso_ids = form.cleaned_data['sso_ids']
        self.remove_collaborator(sso_ids=sso_ids)
        return super().form_valid(form)

    def remove_collaborator(self, sso_ids):
        for sso_id in sso_ids:
            response = api_client.company.collaborator_disconnect(
                sso_session_id=self.request.user.session_id,
                sso_id=sso_id,
            )
            response.raise_for_status()

    def get_success_url(self):
        return settings.SSO_PROFILE_URL + '?user-removed'


class TransferAccountWizardView(
    GetTemplateForCurrentStepMixin, BaseMultiUserAccountManagementView,
    SessionWizardView
):
    EMAIL = 'email'
    PASSWORD = 'password'
    ERROR = 'error'

    form_list = (
        (EMAIL, forms.TransferAccountEmailForm),
        (PASSWORD, forms.TransferAccountPasswordForm),
    )
    templates = {
        EMAIL: 'company-transfer-account-email.html',
        PASSWORD: 'company-transfer-account-password.html',
        ERROR: 'company-transfer-account-error.html',
    }

    def get_form_kwargs(self, step):
        kwargs = super().get_form_kwargs(step)
        if step == self.PASSWORD:
            kwargs['sso_session_id'] = self.request.user.session_id
        elif step == self.EMAIL:
            kwargs['sso_email_address'] = self.request.user.email
        return kwargs

    def done(self, *args, **kwargs):
        email_address = self.get_all_cleaned_data()['email_address']
        self.transfer_owner(email_address=email_address)
        return redirect(self.get_success_url())

    def transfer_owner(self, email_address):
        response = api_client.company.collaborator_invite_create(
            sso_session_id=self.request.user.session_id,
            collaborator_email=email_address,
            role=user_roles.ADMIN,
        )

        if response.status_code == 400:
            if 'collaborator_email' in response.json():
                # email already has a collaboration invite, but do not tell
                # the user to avoid leaking information to bad actors.
                return
        response.raise_for_status()

    def get_success_url(self):
        return settings.SSO_PROFILE_URL + '?owner-transferred'


class BaseAcceptInviteView(FormView):
    form_class = forms.AcceptInviteForm
    success_url = urls.domestic.FIND_A_BUYER
    invalid_template_name = 'company-invite-invalid-token.html'

    def get_initial(self):
        return {
            'invite_key': self.request.GET.get('invite_key')
        }

    @cached_property
    def invite(self):
        response = api_client.company.collaborator_invite_retrieve(self.request.GET.get('invite_key'))
        if response.status_code == 200:
            return response.json()

    def get_template_names(self):
        if not self.invite:
            return ['company-invite-invalid-token.html']
        return super().get_template_names()

    def get_context_data(self, **kwargs):
        return super().get_context_data(invite=self.invite, **kwargs,)

    def form_valid(self, form):
        self.accept_invite(invite_key=form.cleaned_data['invite_key'])
        return super().form_valid(form)

    def accept_invite(self, invite_key):
        response = api_client.company.collaborator_invite_accept(
            sso_session_id=self.request.user.session_id,
            invite_key=invite_key,
        )
        response.raise_for_status()


class AcceptTransferAccountView(BaseAcceptInviteView):
    template_name = 'company-accept-transfer-account.html'


class AcceptCollaborationView(BaseAcceptInviteView):
    template_name = 'company-accept-collaboration.html'


class CSVDumpGenericView(View):

    def get(self, request, *args, **kwargs):
        token = request.GET.get('token')
        if not token:
            return HttpResponseForbidden('Token not provided')
        csv_file = self.get_file(token)
        response = HttpResponse(
            csv_file.content, content_type=csv_file.headers['Content-Type']
        )
        response['Content-Disposition'] = csv_file.headers[
            'Content-Disposition'
        ]
        return response


class BuyerCSVDumpView(CSVDumpGenericView):

    @staticmethod
    def get_file(token):
        return api_client.buyer.get_csv_dump(token)


class SupplierCSVDumpView(CSVDumpGenericView):

    @staticmethod
    def get_file(token):
        return api_client.supplier.get_csv_dump(token)
