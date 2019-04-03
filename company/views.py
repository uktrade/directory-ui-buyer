import os
from urllib.parse import urljoin

from directory_api_client.client import api_client
from directory_constants.constants import urls
from formtools.wizard.views import SessionWizardView
from raven.contrib.django.raven_compat.models import client as sentry_client
from requests.exceptions import HTTPError

from django.conf import settings
from django.core.files.storage import DefaultStorage
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, Http404
from django.template.response import TemplateResponse
from django.utils.functional import cached_property
from django.views.generic import RedirectView, TemplateView, View
from django.views.generic.edit import FormView
from django.urls import reverse, reverse_lazy

from company import forms, helpers, state_requirements
from enrolment.helpers import CompaniesHouseClient


class RedirectNewEditFeatureFlagMixin:
    def get(self, *args, **kwargs):
        if settings.FEATURE_FLAGS['NEW_ACCOUNT_EDIT_ON']:
            return redirect(urls.build_great_url('profile/find-a-buyer/'))
        return super().get(*args, **kwargs)


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
        response = api_client.company.update_profile(
            sso_session_id=self.request.sso_user.session_id,
            data=self.serialize_form_data()
        )
        try:
            response.raise_for_status()
        except HTTPError:
            self.send_update_error_to_sentry(
                sso_user=self.request.sso_user,
                api_response=response
            )
            raise
        else:
            return self.handle_profile_update_success()


class CompanyProfileMixin:

    @cached_property
    def company_profile(self):
        response = api_client.company.retrieve_private_profile(
            sso_session_id=self.request.sso_user.session_id,
        )
        if response.status_code == 404:
            return {}
        response.raise_for_status()
        profile = response.json()

        if profile.get('sectors'):
            profile['sectors'] = profile['sectors'][0]
        return profile


class SupplierProfileMixin:

    @cached_property
    def supplier_profile(self):
        response = api_client.supplier.retrieve_profile(
            sso_session_id=self.request.sso_user.session_id,
        )
        if response.status_code == 404:
            return {}
        response.raise_for_status()
        return response.json()


class GetTemplateForCurrentStepMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.templates

    def get_template_names(self):
        return [self.templates[self.steps.current]]


class BaseMultiStepCompanyEditView(
    state_requirements.UserStateRequirementHandlerMixin,
    CompanyProfileMixin,
    GetTemplateForCurrentStepMixin,
    UpdateCompanyProfileOnFormWizardDoneMixin,
    SessionWizardView
):
    required_user_states = [
        state_requirements.IsLoggedIn,
        state_requirements.HasCompany,
    ]

    def get_form_initial(self, step):
        return self.company_profile


class SupplierCaseStudyWizardView(
    RedirectNewEditFeatureFlagMixin,
    state_requirements.UserStateRequirementHandlerMixin,
    CompanyProfileMixin,
    GetTemplateForCurrentStepMixin,
    SessionWizardView
):
    required_user_states = [
        state_requirements.IsLoggedIn,
        state_requirements.HasCompany,
    ]

    BASIC = 'basic'
    RICH_MEDIA = 'rich-media'

    file_storage = DefaultStorage()

    form_list = (
        (BASIC, forms.CaseStudyBasicInfoForm),
        (RICH_MEDIA, forms.CaseStudyRichMediaForm),
    )
    templates = {
        BASIC: 'supplier-case-study-basic-form.html',
        RICH_MEDIA: 'supplier-case-study-rich-media-form.html',
    }

    form_labels = (
        (BASIC, 'Basic'),
        (RICH_MEDIA, 'Images'),
    )

    form_serializer = staticmethod(forms.serialize_case_study_forms)

    def get_form_initial(self, step):
        if 'id' not in self.kwargs:
            return {}
        response = api_client.company.retrieve_private_case_study(
            sso_session_id=self.request.sso_user.session_id,
            case_study_id=self.kwargs['id'],
        )
        if response.status_code == 404:
            raise Http404()
        response.raise_for_status()
        return response.json()

    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(
            form_labels=self.form_labels, *args, **kwargs
        )

    def serialize_form_data(self):
        return self.form_serializer(self.get_all_cleaned_data())

    def done(self, *args, **kwags):
        data = self.serialize_form_data()
        if 'id' in self.kwargs:
            response = api_client.company.update_case_study(
                data=data,
                case_study_id=self.kwargs['id'],
                sso_session_id=self.request.sso_user.session_id,
            )
        else:
            response = api_client.company.create_case_study(
                sso_session_id=self.request.sso_user.session_id,
                data=data,
            )
        response.raise_for_status()
        return redirect('company-detail')


class CompanyProfileDetailView(
    RedirectNewEditFeatureFlagMixin, CompanyProfileMixin,
    state_requirements.UserStateRequirementHandlerMixin, TemplateView
):
    required_user_states = [
        state_requirements.IsLoggedIn,
        state_requirements.HasCompany,
    ]
    template_name = 'company-profile-detail.html'

    def get_context_data(self, **kwargs):
        profile = helpers.get_company_profile(self.request.sso_user.session_id)
        show_wizard_links = not forms.is_optional_profile_values_set(profile)
        return {
            'company': helpers.format_company_details(profile),
            'show_wizard_links': show_wizard_links,
            'SUPPLIER_SEARCH_URL': settings.SUPPLIER_SEARCH_URL,
        }


class CompanyProfileEditView(
    RedirectNewEditFeatureFlagMixin, BaseMultiStepCompanyEditView
):
    BASIC = 'basic'
    CLASSIFICATION = 'classification'
    SENT = 'sent'

    form_list = (
        (BASIC, forms.CompanyBasicInfoForm),
        (CLASSIFICATION, forms.CompanyClassificationForm),
    )
    form_labels = [
        (BASIC, 'About your company'),
        (CLASSIFICATION, 'Industry and exporting'),
    ]
    templates = {
        BASIC: 'company-profile-form.html',
        CLASSIFICATION: 'company-profile-form-classification.html',
    }

    form_serializer = staticmethod(forms.serialize_company_profile_forms)

    def get_context_data(self, form, **kwargs):
        return super().get_context_data(
            form=form, form_labels=self.form_labels, **kwargs,
        )

    def handle_profile_update_success(self):
        if not self.company_profile['is_verified']:
            return redirect('verify-company-hub')
        return super().handle_profile_update_success()


class SendVerificationLetterView(
    state_requirements.UserStateRequirementHandlerMixin,
    CompanyProfileMixin,
    GetTemplateForCurrentStepMixin,
    UpdateCompanyProfileOnFormWizardDoneMixin,
    SessionWizardView
):
    required_user_states = [
        state_requirements.IsLoggedIn,
        state_requirements.HasUnverifiedCompany,
        state_requirements.VerificationLetterNotSent
    ]

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
        company_address = helpers.build_company_address(self.company_profile)
        return super().get_context_data(
            form=form,
            form_labels=self.form_labels,
            all_cleaned_data=self.get_all_cleaned_data(),
            company_name=self.company_profile['name'],
            company_number=self.company_profile['number'],
            company_address=company_address,
            **kwargs
        )

    def handle_profile_update_success(self):
        return TemplateResponse(self.request, self.templates[self.SENT])


class CompanyProfileLogoEditView(
    RedirectNewEditFeatureFlagMixin, BaseMultiStepCompanyEditView
):
    form_list = (
        ('logo', forms.CompanyLogoForm),
    )
    file_storage = DefaultStorage()
    templates = {
        'logo': 'company-profile-logo-form.html',
    }
    form_serializer = staticmethod(forms.serialize_company_logo_form)


class CompanyVerifyView(
    state_requirements.UserStateRequirementHandlerMixin,
    CompanyProfileMixin,
    TemplateView
):
    required_user_states = [
        state_requirements.IsLoggedIn,
        state_requirements.HasUnverifiedCompany,
        state_requirements.VerificationLetterNotSent,
    ]
    template_name = 'company-verify-hub.html'

    def get_context_data(self, **kwargs):
        return {
            'company': self.company_profile,
        }


class CompanyAddressVerificationView(
    state_requirements.UserStateRequirementHandlerMixin,
    CompanyProfileMixin,
    GetTemplateForCurrentStepMixin,
    SessionWizardView
):
    required_user_states = [
        state_requirements.IsLoggedIn,
        state_requirements.HasUnverifiedCompany,
    ]
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
        kwargs['sso_session_id'] = self.request.sso_user.session_id
        return kwargs

    def done(self, *args, **kwargs):
        return TemplateResponse(
            self.request,
            self.templates[self.SUCCESS]
        )

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            company=self.company_profile,
            **kwargs
        )


class CompanyAddressVerificationHistoricView(RedirectView):
    pattern_name = 'verify-company-address'


class CompanyDescriptionEditView(
    RedirectNewEditFeatureFlagMixin, BaseMultiStepCompanyEditView
):
    DESCRIPTION = 'description'
    form_list = (
        (DESCRIPTION, forms.CompanyDescriptionForm),
    )
    templates = {
        DESCRIPTION: 'company-profile-description-form.html',
    }
    form_serializer = staticmethod(forms.serialize_company_description_form)


class CompanySocialLinksEditView(
    RedirectNewEditFeatureFlagMixin, BaseMultiStepCompanyEditView
):
    SOCIAL = 'social'
    form_list = (
        (SOCIAL, forms.SocialLinksForm),
    )
    templates = {
        SOCIAL: 'company-profile-social-form.html',
    }
    form_serializer = staticmethod(forms.serialize_social_links_form)


class SupplierBasicInfoEditView(
    RedirectNewEditFeatureFlagMixin, BaseMultiStepCompanyEditView
):
    BASIC = 'basic'
    form_list = (
        (BASIC, forms.CompanyBasicInfoForm),
    )
    templates = {
        BASIC: 'company-profile-form.html',
    }
    form_serializer = staticmethod(forms.serialize_company_basic_info_form)


class SupplierClassificationEditView(
    RedirectNewEditFeatureFlagMixin, BaseMultiStepCompanyEditView
):
    CLASSIFICATION = 'classification'
    form_list = (
        (CLASSIFICATION, forms.CompanyClassificationForm),
    )
    templates = {
        CLASSIFICATION: 'company-profile-form-classification.html',
    }
    form_serializer = staticmethod(forms.serialize_company_sectors_form)


class SupplierContactEditView(
    RedirectNewEditFeatureFlagMixin, BaseMultiStepCompanyEditView
):
    CONTACT = 'contact'
    form_list = (
        (CONTACT, forms.CompanyContactDetailsForm),
    )
    templates = {
        CONTACT: 'company-profile-form-contact.html',
    }
    form_serializer = staticmethod(forms.serialize_company_contact_form)


class SupplierAddressEditView(
    RedirectNewEditFeatureFlagMixin, BaseMultiStepCompanyEditView
):
    ADDRESS = 'address'
    form_list = (
        (ADDRESS, forms.CompanyAddressVerificationForm),
    )
    templates = {
        ADDRESS: 'company-profile-form-address.html',
    }
    form_serializer = staticmethod(forms.serialize_company_address_form)

    def get_context_data(self, form, **kwargs):
        company_address = helpers.build_company_address(self.company_profile)
        return super().get_context_data(
            form=form,
            company_name=self.company_profile['name'],
            company_number=self.company_profile['number'],
            company_address=company_address,
            **kwargs,
        )


class EmailUnsubscribeView(
    state_requirements.UserStateRequirementHandlerMixin, FormView
):

    required_user_states = [
        state_requirements.IsLoggedIn
    ]

    form_class = forms.EmptyForm
    template_name = 'email-unsubscribe.html'
    success_template = 'email-unsubscribe-success.html'

    def form_valid(self, form):
        response = api_client.supplier.unsubscribe(
            sso_session_id=self.request.sso_user.session_id
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
        callback_url = reverse('verify-companies-house-callback')
        if settings.FEATURE_URL_PREFIX_ENABLED:
            return urljoin(
                settings.COMPANIES_HOUSE_CALLBACK_DOMAIN,
                callback_url.replace('/find-a-buyer', '', 1)
            )
        return self.request.build_absolute_uri(callback_url)


class CompaniesHouseOauth2View(
    state_requirements.UserStateRequirementHandlerMixin,
    CompanyProfileMixin,
    Oauth2CallbackUrlMixin,
    RedirectView
):
    required_user_states = [
        state_requirements.IsLoggedIn,
        state_requirements.HasUnverifiedCompany,
    ]

    def get_redirect_url(self):
        company = helpers.get_company_profile(self.request.sso_user.session_id)
        return CompaniesHouseClient.make_oauth2_url(
            company_number=company['number'],
            redirect_uri=self.redirect_uri,
        )


class CompaniesHouseOauth2CallbackView(
    state_requirements.UserStateRequirementHandlerMixin,
    CompanyProfileMixin,
    SubmitFormOnGetMixin,
    Oauth2CallbackUrlMixin,
    FormView
):
    required_user_states = [
        state_requirements.IsLoggedIn,
        state_requirements.HasUnverifiedCompany,
    ]

    form_class = forms.CompaniesHouseOauth2Form
    template_name = 'companies-house-oauth2-callback.html'
    error_template = 'companies-house-oauth2-error.html'
    success_url = reverse_lazy('company-detail')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['redirect_uri'] = self.redirect_uri
        return kwargs

    def form_valid(self, form):
        response = api_client.company.verify_with_companies_house(
            sso_session_id=self.request.sso_user.session_id,
            access_token=form.oauth2_response.json()['access_token']
        )
        if response.status_code == 500:
            return TemplateResponse(self.request, self.error_template)
        else:
            return super().form_valid(form)


class BaseMultiUserAccountManagementView(
    CompanyProfileMixin, SupplierProfileMixin,
    state_requirements.UserStateRequirementHandlerMixin,
):
    required_user_states = [
        state_requirements.IsLoggedIn,
        state_requirements.IsCompanyOwner,
    ]

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
            'sso_email_address': self.request.sso_user.email
        }

    def get_initial(self):
        initial = super().get_initial()
        initial["email_address"] = self.request.GET.get('email')
        return initial

    def form_valid(self, form):
        self.add_collaborator(email_address=form.cleaned_data['email_address'])
        return super().form_valid(form)

    def add_collaborator(self, email_address):
        response = api_client.company.create_collaboration_invite(
            sso_session_id=self.request.sso_user.session_id,
            collaborator_email=email_address,
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
            'sso_session_id': self.request.sso_user.session_id,
            **form_kwargs
        }

    def form_valid(self, form):
        sso_ids = form.cleaned_data['sso_ids']
        self.remove_collaborator(sso_ids=sso_ids)
        return super().form_valid(form)

    def remove_collaborator(self, sso_ids):
        response = api_client.company.remove_collaborators(
            sso_session_id=self.request.sso_user.session_id,
            sso_ids=sso_ids,
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
            kwargs['sso_session_id'] = self.request.sso_user.session_id
        elif step == self.EMAIL:
            kwargs['sso_email_address'] = self.request.sso_user.email
        return kwargs

    def done(self, *args, **kwargs):
        email_address = self.get_all_cleaned_data()['email_address']
        self.transfer_owner(email_address=email_address)
        return redirect(self.get_success_url())

    def transfer_owner(self, email_address):
        response = api_client.company.create_transfer_invite(
            sso_session_id=self.request.sso_user.session_id,
            new_owner_email=email_address,
        )

        if response.status_code == 400:
            if 'new_owner_email' in response.json():
                # email already has a collaboration invite, but do not tell
                # the user to avoid leaking information to bad actors.
                return
        response.raise_for_status()

    def get_success_url(self):
        return settings.SSO_PROFILE_URL + '?owner-transferred'


class BaseAcceptInviteView(
    CompanyProfileMixin, state_requirements.UserStateRequirementHandlerMixin,
    FormView
):
    form_class = forms.AcceptInviteForm
    success_url = reverse_lazy('company-detail')
    invalid_template_name = 'company-invite-invalid-token.html'

    def get_initial(self):
        return {
            'invite_key': self.request.GET.get('invite_key')
        }

    @cached_property
    def invite(self):
        response = self.retrieve_api_method(
            sso_session_id=self.request.sso_user.session_id,
            invite_key=self.request.GET.get('invite_key'),
        )
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
        response = self.accept_api_method(
            sso_session_id=self.request.sso_user.session_id,
            invite_key=invite_key,
        )
        response.raise_for_status()


class AcceptTransferAccountView(SupplierProfileMixin, BaseAcceptInviteView):

    template_name = 'company-accept-transfer-account.html'
    retrieve_api_method = api_client.company.retrieve_transfer_invite
    accept_api_method = api_client.company.accept_transfer_invite
    required_user_states = [
        state_requirements.IsLoggedIn,
        state_requirements.NotCompanyOwner,
    ]


class AcceptCollaborationView(BaseAcceptInviteView):

    template_name = 'company-accept-collaboration.html'
    retrieve_api_method = api_client.company.retrieve_collaboration_invite
    accept_api_method = api_client.company.accept_collaboration_invite
    required_user_states = [
        state_requirements.IsLoggedIn,
        state_requirements.NoCompany,
    ]


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
