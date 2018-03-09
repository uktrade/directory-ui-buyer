import os

from django.http import HttpResponse, HttpResponseForbidden
from formtools.wizard.views import SessionWizardView

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import redirect, Http404
from django.template.response import TemplateResponse
from django.utils.functional import cached_property
from django.views.generic import RedirectView, TemplateView, View
from django.views.generic.edit import FormView

from api_client import api_client
from company import forms, helpers
from enrolment.helpers import CompaniesHouseClient, has_company
from sso.utils import SSOLoginRequiredMixin


class CompanyStateRequirement(SSOLoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.sso_user is None:
            return self.handle_no_permission()
        if not self.is_company_state_valid():
            return redirect(self.redirect_name)
        return super().dispatch(request, *args, **kwargs)


class CompanyRequiredMixin(CompanyStateRequirement):
    redirect_name = 'index'

    def is_company_state_valid(self):
        return has_company(self.request.sso_user.session_id)


class NoCompanyRequiredMixin(CompanyStateRequirement):
    redirect_name = 'company-detail'

    def is_company_state_valid(self):
        return not has_company(self.request.sso_user.session_id)


class UnverifiedCompanyRequiredMixin(CompanyStateRequirement):

    @property
    def redirect_name(self):
        if self.has_company:
            return 'company-detail'
        return 'index'

    def is_company_verified(self):
        return self.company_profile['is_verified']

    @cached_property
    def has_company(self):
        return has_company(self.request.sso_user.session_id)

    def is_company_state_valid(self):
        return self.has_company and not self.is_company_verified()


class VerificationLetterNotSentRequiredMixin(UnverifiedCompanyRequiredMixin):

    def is_letter_sent(self):
        return self.company_profile['is_verification_letter_sent']

    @property
    def redirect_name(self):
        if self.has_company and self.is_letter_sent():
            return 'verify-company-address-confirm'
        return super().redirect_name

    def is_company_state_valid(self):
        return super().is_company_state_valid() and not self.is_letter_sent()


class SupplierStateRequirement(SSOLoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.sso_user is None:
            return self.handle_no_permission()
        if not self.is_supplier_state_valid():
            return redirect('company-detail')
        return super().dispatch(request, *args, **kwargs)

    def has_company(self):
        return has_company(self.request.sso_user.session_id)

    @property
    def supplier_profile(self):
        response = api_client.supplier.retrieve_profile(
            sso_session_id=self.request.sso_user.session_id,
        )
        if response.status_code == 404:
            return {}
        response.raise_for_status()
        return response.json()


class CompanyOwnerRequiredMixin(SupplierStateRequirement):
    def is_supplier_state_valid(self):
        profile = self.supplier_profile
        return profile and profile['is_company_owner']


class NotCompanyOwnerRequiredMixin(SupplierStateRequirement):
    def is_supplier_state_valid(self):
        profile = self.supplier_profile
        return not profile or not profile['is_company_owner']


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

    def handle_profile_update_failure(self):
        return TemplateResponse(self.request, self.failure_template)

    def done(self, *args, **kwargs):
        api_response = api_client.company.update_profile(
            sso_session_id=self.request.sso_user.session_id,
            data=self.serialize_form_data()
        )
        if api_response.ok:
            response = self.handle_profile_update_success()
        else:
            response = self.handle_profile_update_failure()
        return response


class CompanyProfileMixin:

    @cached_property
    def company_profile(self):
        profile = helpers.get_company_profile(self.request.sso_user.session_id)
        if profile['sectors']:
            profile['sectors'] = profile['sectors'][0]
        return profile


class GetTemplateForCurrentStepMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.templates

    def get_template_names(self):
        return [self.templates[self.steps.current]]


class NotFoundOnDisabledFeature:

    def dispatch(self, *args, **kwargs):
        if not self.flag:
            raise Http404()
        return super().dispatch(*args, **kwargs)


class Oauth2FeatureFlagMixin(NotFoundOnDisabledFeature):

    @property
    def flag(self):
        return settings.FEATURE_COMPANIES_HOUSE_OAUTH2_ENABLED


class MultiUserAccountFeatureFlagMixin(NotFoundOnDisabledFeature):

    @property
    def flag(self):
        return settings.FEATURE_MULTI_USER_ACCOUNT_ENABLED


class BaseMultiStepCompanyEditView(
    CompanyRequiredMixin,
    CompanyProfileMixin,
    GetTemplateForCurrentStepMixin,
    UpdateCompanyProfileOnFormWizardDoneMixin,
    SessionWizardView
):
    def get_form_initial(self, step):
        return self.company_profile


class SupplierCaseStudyWizardView(
    CompanyRequiredMixin,
    GetTemplateForCurrentStepMixin,
    SessionWizardView
):

    BASIC = 'basic'
    RICH_MEDIA = 'rich-media'

    failure_template = 'supplier-case-study-error.html'

    file_storage = FileSystemStorage(
        location=os.path.join(settings.MEDIA_ROOT, 'tmp-supplier-media')
    )

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
        if response.ok:
            return redirect('company-detail')
        else:
            return TemplateResponse(self.request, self.failure_template)


class CompanyProfileDetailView(CompanyRequiredMixin, TemplateView):
    template_name = 'company-profile-detail.html'

    def get_context_data(self, **kwargs):
        profile = helpers.get_company_profile(self.request.sso_user.session_id)
        show_wizard_links = not forms.is_optional_profile_values_set(profile)
        return {
            'company': helpers.format_company_details(profile),
            'show_wizard_links': show_wizard_links,
            'SUPPLIER_SEARCH_URL': settings.SUPPLIER_SEARCH_URL,
        }


class CompanyProfileEditView(BaseMultiStepCompanyEditView):
    ADDRESS = 'address'
    BASIC = 'basic'
    CLASSIFICATION = 'classification'
    SENT = 'sent'

    form_list = (
        (BASIC, forms.CompanyBasicInfoForm),
        (CLASSIFICATION, forms.CompanyClassificationForm),
        (ADDRESS, forms.CompanyAddressVerificationForm),
    )
    templates = {
        BASIC: 'company-profile-form.html',
        CLASSIFICATION: 'company-profile-form-classification.html',
        ADDRESS: 'company-profile-form-address.html',
        SENT: 'company-profile-form-letter-sent.html',
    }

    failure_template = 'company-profile-update-error.html'

    @property
    def form_labels(self):
        labels = [
            (self.BASIC, 'About your company'),
            (self.CLASSIFICATION, 'Industry and exporting'),
        ]
        if self.condition_show_address():
            labels.append((self.ADDRESS, 'Review and send'))
        return labels

    def render_next_step(self, form, **kwargs):
        # when the final step is posted, formtools `current_step` is
        # "address". However, `form_labels` does not return "confirm" because
        # the letter has now been sent - resulting in ValueError
        # https://sentry.ci.uktrade.io/dit/directory-ui-buyer-dev/issues/1588/
        if self.steps.current == self.ADDRESS:
            if not self.condition_show_address():
                return self.render_done(form, **kwargs)
        return super().render_next_step(form, **kwargs)

    def condition_show_address(self):
        # once this feature flag is removed, this view will never show address
        if settings.FEATURE_COMPANIES_HOUSE_OAUTH2_ENABLED:
            return False
        return not any([
            self.company_profile['is_verification_letter_sent'],
            self.company_profile['verified_with_preverified_enrolment'],
        ])

    condition_dict = {
        ADDRESS: condition_show_address,
    }

    @property
    def form_serializer(self):
        if self.condition_show_address():
            return forms.serialize_company_profile_forms
        return forms.serialize_company_profile_without_address_forms

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(
            form=form, form_labels=self.form_labels, **kwargs,
        )
        if self.steps.current == self.ADDRESS:
            all_cleaned_data = self.get_all_cleaned_data()
            context['company_name'] = all_cleaned_data.get('name')
            context['company_number'] = self.company_profile['number']
            context['company_address'] = helpers.build_company_address(
                self.company_profile
            )
        return context

    def handle_profile_update_success(self):
        if settings.FEATURE_COMPANIES_HOUSE_OAUTH2_ENABLED:
            if not self.company_profile['is_verified']:
                return redirect('verify-company-hub')
        elif self.condition_show_address():
            return TemplateResponse(self.request, self.templates[self.SENT])
        return super().handle_profile_update_success()


class SendVerificationLetterView(
    Oauth2FeatureFlagMixin,
    CompanyProfileMixin,
    UnverifiedCompanyRequiredMixin,
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
    failure_template = 'company-profile-update-error.html'

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


class CompanyProfileLogoEditView(BaseMultiStepCompanyEditView):
    form_list = (
        ('logo', forms.CompanyLogoForm),
    )
    file_storage = FileSystemStorage(
        location=os.path.join(settings.MEDIA_ROOT, 'tmp-logos')
    )
    failure_template = 'company-profile-update-error.html'
    templates = {
        'logo': 'company-profile-logo-form.html',
    }
    form_serializer = staticmethod(forms.serialize_company_logo_form)


class CompanyVerifyView(
    Oauth2FeatureFlagMixin,
    CompanyProfileMixin,
    VerificationLetterNotSentRequiredMixin,
    TemplateView
):
    template_name = 'company-verify-hub.html'

    def get_context_data(self, **kwargs):
        return {
            'company': self.company_profile,
        }


class CompanyAddressVerificationView(
    CompanyProfileMixin,
    UnverifiedCompanyRequiredMixin,
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
        kwargs['sso_session_id'] = self.request.sso_user.session_id
        return kwargs

    def done(self, *args, **kwargs):
        return TemplateResponse(
            self.request,
            self.templates[self.SUCCESS]
        )


# once the feature flag is removed, turn this into a RedirectView
class CompanyAddressVerificationHistoricView(CompanyAddressVerificationView):
    def dispatch(self, *args, **kwargs):
        if settings.FEATURE_COMPANIES_HOUSE_OAUTH2_ENABLED:
            # redirect to the same view, bit with the new url
            return redirect('verify-company-address')
        return super().dispatch(*args, **kwargs)


class CompanyDescriptionEditView(BaseMultiStepCompanyEditView):
    DESCRIPTION = 'description'
    form_list = (
        (DESCRIPTION, forms.CompanyDescriptionForm),
    )
    failure_template = 'company-profile-update-error.html'
    templates = {
        DESCRIPTION: 'company-profile-description-form.html',
    }
    form_serializer = staticmethod(forms.serialize_company_description_form)


class CompanySocialLinksEditView(BaseMultiStepCompanyEditView):
    SOCIAL = 'social'
    form_list = (
        (SOCIAL, forms.SocialLinksForm),
    )
    failure_template = 'company-profile-update-error.html'
    templates = {
        SOCIAL: 'company-profile-social-form.html',
    }
    form_serializer = staticmethod(forms.serialize_social_links_form)


class SupplierBasicInfoEditView(BaseMultiStepCompanyEditView):
    BASIC = 'basic'
    form_list = (
        (BASIC, forms.CompanyBasicInfoForm),
    )
    failure_template = 'company-profile-update-error.html'
    templates = {
        BASIC: 'company-profile-form.html',
    }
    form_serializer = staticmethod(forms.serialize_company_basic_info_form)


class SupplierClassificationEditView(BaseMultiStepCompanyEditView):
    CLASSIFICATION = 'classification'
    form_list = (
        (CLASSIFICATION, forms.CompanyClassificationForm),
    )
    templates = {
        CLASSIFICATION: 'company-profile-form-classification.html',
    }
    failure_template = 'company-profile-update-error.html'
    form_serializer = staticmethod(forms.serialize_company_sectors_form)


class SupplierContactEditView(BaseMultiStepCompanyEditView):
    CONTACT = 'contact'
    form_list = (
        (CONTACT, forms.CompanyContactDetailsForm),
    )
    failure_template = 'company-profile-update-error.html'
    templates = {
        CONTACT: 'company-profile-form-contact.html',
    }
    form_serializer = staticmethod(forms.serialize_company_contact_form)


class SupplierAddressEditView(BaseMultiStepCompanyEditView):
    ADDRESS = 'address'
    form_list = (
        (ADDRESS, forms.CompanyAddressVerificationForm),
    )
    failure_template = 'company-profile-update-error.html'
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


class EmailUnsubscribeView(SSOLoginRequiredMixin, FormView):
    form_class = forms.EmptyForm
    template_name = 'email-unsubscribe.html'
    success_template = 'email-unsubscribe-success.html'
    failure_template = 'email-unsubscribe-error.html'

    def form_valid(self, form):
        response = api_client.supplier.unsubscribe(
            sso_session_id=self.request.sso_user.session_id
        )
        if response.ok:
            return TemplateResponse(self.request, self.success_template)
        return TemplateResponse(self.request, self.failure_template)


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
        return self.request.build_absolute_uri(callback_url)


class CompaniesHouseOauth2View(
    Oauth2FeatureFlagMixin,
    CompanyProfileMixin,
    UnverifiedCompanyRequiredMixin,
    Oauth2CallbackUrlMixin,
    RedirectView
):

    def get_redirect_url(self):
        company = helpers.get_company_profile(self.request.sso_user.session_id)
        return CompaniesHouseClient.make_oauth2_url(
            company_number=company['number'],
            redirect_uri=self.redirect_uri,
        )


class CompaniesHouseOauth2CallbackView(
    Oauth2FeatureFlagMixin,
    CompanyProfileMixin,
    UnverifiedCompanyRequiredMixin,
    SubmitFormOnGetMixin,
    Oauth2CallbackUrlMixin,
    FormView
):
    form_class = forms.CompaniesHouseOauth2Form
    template_name = 'companies-house-oauth2-callback.html'
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
        response.raise_for_status()
        return super().form_valid(form)


class BaseMultiUserAccountManagementView(
    MultiUserAccountFeatureFlagMixin, CompanyRequiredMixin,
    CompanyOwnerRequiredMixin
):
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
            'sso_email_address': self.request.sso_user.email,
        }

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
    failure_template = 'company-transfer-error.html'
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
    MultiUserAccountFeatureFlagMixin, NotCompanyOwnerRequiredMixin, FormView
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
        if response.ok:
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


class AcceptTransferAccountView(BaseAcceptInviteView):
    template_name = 'company-accept-transfer-account.html'
    retrieve_api_method = api_client.company.retrieve_transfer_invite
    accept_api_method = api_client.company.accept_transfer_invite


class AcceptCollaborationView(BaseAcceptInviteView):
    template_name = 'company-accept-collaboration.html'
    retrieve_api_method = api_client.company.retrieve_collaboration_invite
    accept_api_method = api_client.company.accept_collaboration_invite


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
