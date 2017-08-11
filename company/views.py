import os

from formtools.wizard.views import SessionWizardView

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import redirect, Http404
from django.template.response import TemplateResponse
from django.utils.functional import cached_property
from django.views.generic import RedirectView, TemplateView
from django.views.generic.edit import FormView

from api_client import api_client
from company import forms, helpers
from enrolment.helpers import CompaniesHouseClient, has_company
from sso.utils import SSOLoginRequiredMixin


class CompanyRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.sso_user is None:
            return self.handle_no_permission()
        else:
            if not has_company(self.request.sso_user.session_id):
                # the landing page has an input box for enrolling the company
                return redirect('index')
            else:
                return super().dispatch(request, *args, **kwargs)


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


class GetCompanyProfileInitialFormDataMixin:
    def get_form_initial(self, step):
        return helpers.get_company_profile(self.request.sso_user.session_id)


class GetTemplateForCurrentStepMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.templates

    def get_template_names(self):
        return [self.templates[self.steps.current]]


class Oauth2FeatureFlagMixin:
    def dispatch(self, *args, **kwargs):
        if not settings.FEATURE_COMPANIES_HOUSE_OAUTH2_ENABLED:
            raise Http404()
        return super().dispatch(*args, **kwargs)


class BaseMultiStepCompanyEditView(
    SSOLoginRequiredMixin,
    CompanyRequiredMixin,
    GetTemplateForCurrentStepMixin,
    UpdateCompanyProfileOnFormWizardDoneMixin,
    SessionWizardView
):
    pass


class SupplierCaseStudyWizardView(
    SSOLoginRequiredMixin,
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
        if not self.kwargs['id']:
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
        if self.kwargs['id']:
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


class CompanyProfileDetailView(
    SSOLoginRequiredMixin, CompanyRequiredMixin, TemplateView
):
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
    ADDRESS_CONFIRM = 'confirm'
    SENT = 'sent'

    form_list = (
        (BASIC, forms.CompanyBasicInfoForm),
        (CLASSIFICATION, forms.CompanyClassificationForm),
        (ADDRESS, forms.CompanyAddressVerificationForm),
        (ADDRESS_CONFIRM, forms.EmptyForm),
    )
    templates = {
        BASIC: 'company-profile-form.html',
        CLASSIFICATION: 'company-profile-form-classification.html',
        ADDRESS: 'company-profile-form-address.html',
        ADDRESS_CONFIRM: 'company-profile-address-confirm-send.html',
        SENT: 'company-profile-form-letter-sent.html',
    }
    failure_template = 'company-profile-update-error.html'

    @property
    def form_labels(self):
        labels = [
            (self.BASIC, 'Basic'),
            (self.CLASSIFICATION, 'Industry and exporting'),
        ]
        if self.condition_show_address():
            labels += [
                (self.ADDRESS, 'Address'),
                (self.ADDRESS_CONFIRM, 'Confirm'),
            ]
        return labels

    def render_next_step(self, form, **kwargs):
        # when the final step is posted, formtools `current_step` is
        # "confirm". However, `form_labels` does not return "confirm" because
        # the letter has now been sent - resulting in ValueError
        # https://sentry.ci.uktrade.io/dit/directory-ui-buyer-dev/issues/1588/
        if self.steps.current == self.ADDRESS_CONFIRM:
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
        ADDRESS_CONFIRM: condition_show_address,
    }

    @property
    def form_serializer(self):
        if self.condition_show_address():
            return forms.serialize_company_profile_forms
        return forms.serialize_company_profile_without_address_forms

    @cached_property
    def company_profile(self):
        profile = helpers.get_company_profile(self.request.sso_user.session_id)
        if profile['sectors']:
            profile['sectors'] = profile['sectors'][0]
        return profile

    def get_form_initial(self, step):
        if step == self.ADDRESS:
            sso_session_id = self.request.sso_user.session_id
            return helpers.get_contact_details(sso_session_id)
        return self.company_profile

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(
            form=form, form_labels=self.form_labels, **kwargs
        )
        if self.steps.current == self.ADDRESS_CONFIRM:
            context['all_cleaned_data'] = self.get_all_cleaned_data()
        return context

    def handle_profile_update_success(self):
        if self.condition_show_address():
            return TemplateResponse(self.request, self.templates[self.SENT])
        return super().handle_profile_update_success()


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
    Oauth2FeatureFlagMixin, SSOLoginRequiredMixin, CompanyRequiredMixin,
    TemplateView,
):
    template_name = 'company-verify.html'


class CompanyAddressVerificationView(
    SSOLoginRequiredMixin,
    CompanyRequiredMixin,
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


# TODO: once the feature flag is removed, turn this into a RedirectView
class CompanyAddressVerificationHistoricView(CompanyAddressVerificationView):
    def dispatch(self, *args, **kwargs):
        if settings.FEATURE_COMPANIES_HOUSE_OAUTH2_ENABLED:
            # redirect to the same view, bit with the new url
            return redirect('verify-company-address')
        return super().dispatch(*args, **kwargs)


class CompanyDescriptionEditView(
    GetCompanyProfileInitialFormDataMixin, BaseMultiStepCompanyEditView
):
    DESCRIPTION = 'description'
    form_list = (
        (DESCRIPTION, forms.CompanyDescriptionForm),
    )
    failure_template = 'company-profile-update-error.html'
    templates = {
        DESCRIPTION: 'company-profile-description-form.html',
    }
    form_serializer = staticmethod(forms.serialize_company_description_form)


class CompanySocialLinksEditView(
    GetCompanyProfileInitialFormDataMixin, BaseMultiStepCompanyEditView
):
    SOCIAL = 'social'
    form_list = (
        (SOCIAL, forms.SocialLinksForm),
    )
    failure_template = 'company-profile-update-error.html'
    templates = {
        SOCIAL: 'company-profile-social-form.html',
    }
    form_serializer = staticmethod(forms.serialize_social_links_form)


class SupplierBasicInfoEditView(
    GetCompanyProfileInitialFormDataMixin, BaseMultiStepCompanyEditView
):
    BASIC = 'basic'
    form_list = (
        (BASIC, forms.CompanyBasicInfoForm),
    )
    failure_template = 'company-profile-update-error.html'
    templates = {
        BASIC: 'company-profile-form.html',
    }
    form_serializer = staticmethod(forms.serialize_company_basic_info_form)


class SupplierClassificationEditView(
    GetCompanyProfileInitialFormDataMixin, BaseMultiStepCompanyEditView
):
    CLASSIFICATION = 'classification'
    form_list = (
        (CLASSIFICATION, forms.CompanyClassificationForm),
    )
    templates = {
        CLASSIFICATION: 'company-profile-form-classification.html',
    }
    failure_template = 'company-profile-update-error.html'
    form_serializer = staticmethod(forms.serialize_company_sectors_form)


class SupplierContactEditView(
    GetCompanyProfileInitialFormDataMixin, BaseMultiStepCompanyEditView
):
    CONTACT = 'contact'
    form_list = (
        (CONTACT, forms.CompanyContactDetailsForm),
    )
    failure_template = 'company-profile-update-error.html'
    templates = {
        CONTACT: 'company-profile-form-contact.html',
    }
    form_serializer = staticmethod(forms.serialize_company_contact_form)

    def get_form_initial(self, step):
        sso_session_id = self.request.sso_user.session_id
        return helpers.get_contact_details(sso_session_id=sso_session_id)


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

    def get_form_initial(self, step):
        sso_session_id = self.request.sso_user.session_id
        return helpers.get_contact_details(sso_session_id=sso_session_id)


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
    Oauth2FeatureFlagMixin, SSOLoginRequiredMixin, CompanyRequiredMixin,
    Oauth2CallbackUrlMixin, RedirectView
):

    def get_redirect_url(self):
        company = helpers.get_company_profile(self.request.sso_user.session_id)
        return CompaniesHouseClient.make_oauth2_url(
            company_number=company['number'],
            redirect_uri=self.redirect_uri,
        )


class CompaniesHouseOauth2CallbackView(
    Oauth2FeatureFlagMixin, SSOLoginRequiredMixin, CompanyRequiredMixin,
    SubmitFormOnGetMixin, Oauth2CallbackUrlMixin, FormView
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
            access_token=form.oauth2_response.json()['access-token']
        )
        response.raise_for_status()
        return super().form_valid(form)
