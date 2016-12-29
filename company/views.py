import os

from formtools.wizard.views import SessionWizardView

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views.generic import TemplateView

from api_client import api_client
from company import forms, helpers
from enrolment.helpers import has_company
from sso.utils import SSOLoginRequiredMixin


class SupplierCompanyBaseView(SSOLoginRequiredMixin):

    def dispatch(self, request, *args, **kwargs):
        if request.sso_user is None:
            return self.handle_no_permission()
        else:
            if not has_company(self.request.sso_user.id):
                return redirect('register-instructions')
            else:
                return super(SupplierCompanyBaseView, self).dispatch(
                    request, *args, **kwargs
                )


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
            sso_user_id=self.request.sso_user.id,
            data=self.serialize_form_data()
        )
        if api_response.ok:
            response = self.handle_profile_update_success()
        else:
            response = self.handle_profile_update_failure()
        return response


class GetCompanyProfileInitialFormDataMixin:
    def get_form_initial(self, step):
        sso_user_id = self.request.sso_user.id
        response = api_client.company.retrieve_profile(sso_user_id)
        if not response.ok:
            response.raise_for_status()
        return response.json()


class GetTemplateForCurrentStepMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.templates

    def get_template_names(self):
        return [self.templates[self.steps.current]]


class SupplierCaseStudyWizardView(
    SupplierCompanyBaseView,
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
    form_serializer = staticmethod(forms.serialize_supplier_case_study_forms)

    def get_form_initial(self, step):
        if not self.kwargs['id']:
            return {}
        response = api_client.company.retrieve_supplier_case_study(
            sso_user_id=self.request.sso_user.id,
            case_study_id=self.kwargs['id'],
        )
        if not response.ok:
            response.raise_for_status()
        return response.json()

    def serialize_form_data(self):
        return self.form_serializer(self.get_all_cleaned_data())

    def done(self, *args, **kwags):
        data = self.serialize_form_data()
        if self.kwargs['id']:
            response = api_client.company.update_supplier_case_study(
                data=data,
                case_study_id=self.kwargs['id'],
                sso_user_id=self.request.sso_user.id,
            )
        else:
            response = api_client.company.create_supplier_case_study(
                sso_user_id=self.request.sso_user.id,
                data=data,
            )
        if response.ok:
            return redirect('company-detail')
        else:
            return TemplateResponse(self.request, self.failure_template)


class SupplierCompanyProfileDetailView(SupplierCompanyBaseView, TemplateView):
    template_name = 'company-private-profile-detail.html'

    def get_context_data(self, **kwargs):
        response = api_client.company.retrieve_profile(
            sso_user_id=self.request.sso_user.id
        )
        if not response.ok:
            response.raise_for_status()
        profile = helpers.get_company_profile_from_response(response)
        show_wizard_links = not forms.is_optional_profile_values_set(profile)
        return {
            'company': profile,
            'show_wizard_links': show_wizard_links,
        }


class SupplierCompanyProfileEditView(
    SupplierCompanyBaseView,
    GetTemplateForCurrentStepMixin,
    UpdateCompanyProfileOnFormWizardDoneMixin,
    SessionWizardView
):
    ADDRESS = 'address'
    BASIC = 'basic'
    CLASSIFICATION = 'classification'
    CONTACT = 'contact'
    ADDRESS_CONFIRM = 'confirm'
    SENT = 'sent'

    form_list = (
        (BASIC, forms.CompanyBasicInfoForm),
        (CLASSIFICATION, forms.CompanyClassificationForm),
        (CONTACT, forms.CompanyContactDetailsForm),
        (ADDRESS, forms.CompanyAddressVerificationForm),
        (ADDRESS_CONFIRM, forms.EmptyForm),
    )
    templates = {
        BASIC: 'company-profile-form.html',
        CLASSIFICATION: 'company-profile-form-classification.html',
        CONTACT: 'company-profile-form-contact.html',
        ADDRESS: 'company-profile-form-address.html',
        ADDRESS_CONFIRM: 'company-profile-address-confirm-send.html',
        SENT: 'company-profile-form-letter-sent.html',
    }
    failure_template = 'company-profile-update-error.html'
    form_serializer = staticmethod(forms.serialize_company_profile_forms)

    def dispatch(self, request, *args, **kwargs):
        sso_user_id = request.sso_user.id
        self.company_profile = helpers.get_company_profile(sso_user_id)
        return super().dispatch(request, *args, **kwargs)

    def condition_show_address(self):
        return not self.company_profile['is_verification_letter_sent']

    condition_dict = {
        ADDRESS_CONFIRM: condition_show_address,
    }

    def get_form_initial(self, step):
        if step in [self.ADDRESS, self.CONTACT]:
            sso_user_id = self.request.sso_user.id
            return helpers.get_contact_details(sso_user_id)
        return self.company_profile

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        if self.steps.current == self.ADDRESS_CONFIRM:
            context['all_cleaned_data'] = self.get_all_cleaned_data()
        return context

    def handle_profile_update_success(self):
        if self.condition_show_address():
            return TemplateResponse(self.request, self.templates[self.SENT])
        return super().handle_profile_update_success()


class SupplierCompanyProfileLogoEditView(
    SupplierCompanyBaseView,
    GetTemplateForCurrentStepMixin,
    UpdateCompanyProfileOnFormWizardDoneMixin,
    SessionWizardView
):

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


class SupplierCompanyAddressVerificationView(
    SupplierCompanyBaseView,
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
        kwargs['sso_id'] = self.request.sso_user.id
        return kwargs

    def done(self, *args, **kwargs):
        return TemplateResponse(
            self.request,
            self.templates[self.SUCCESS]
        )


class SupplierCompanyDescriptionEditView(
    SupplierCompanyBaseView,
    GetTemplateForCurrentStepMixin,
    GetCompanyProfileInitialFormDataMixin,
    UpdateCompanyProfileOnFormWizardDoneMixin,
    SessionWizardView
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


class SupplierCompanySocialLinksEditView(
    SupplierCompanyBaseView,
    GetTemplateForCurrentStepMixin,
    GetCompanyProfileInitialFormDataMixin,
    UpdateCompanyProfileOnFormWizardDoneMixin,
    SessionWizardView
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
    SupplierCompanyBaseView,
    GetTemplateForCurrentStepMixin,
    GetCompanyProfileInitialFormDataMixin,
    UpdateCompanyProfileOnFormWizardDoneMixin,
    SessionWizardView
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
    SupplierCompanyBaseView,
    GetTemplateForCurrentStepMixin,
    GetCompanyProfileInitialFormDataMixin,
    UpdateCompanyProfileOnFormWizardDoneMixin,
    SessionWizardView
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
    SupplierCompanyBaseView,
    GetTemplateForCurrentStepMixin,
    GetCompanyProfileInitialFormDataMixin,
    UpdateCompanyProfileOnFormWizardDoneMixin,
    SessionWizardView
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
        sso_user_id = self.request.sso_user.id
        return helpers.get_contact_details(sso_user_id)


class SupplierAddressEditView(
    SupplierCompanyBaseView,
    GetTemplateForCurrentStepMixin,
    UpdateCompanyProfileOnFormWizardDoneMixin,
    SessionWizardView
):
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
        sso_user_id = self.request.sso_user.id
        return helpers.get_contact_details(sso_user_id)
