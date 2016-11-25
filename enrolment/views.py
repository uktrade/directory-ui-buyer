import logging
import os

from formtools.wizard.views import NamedUrlSessionWizardView, SessionWizardView

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.cache import patch_response_headers
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.views.generic.base import View

from api_client import api_client
from enrolment import forms, helpers
from enrolment import constants
from sso.utils import SSOLoginRequiredMixin


logger = logging.getLogger(__name__)


class CacheMixin:

    def render_to_response(self, context, **response_kwargs):
        # Get response from parent TemplateView class
        response = super().render_to_response(
            context, **response_kwargs
        )

        # Add Cache-Control and Expires headers
        patch_response_headers(response, cache_timeout=60 * 30)

        # Return response
        return response


class CachableTemplateView(CacheMixin, TemplateView):
    pass


class DomesticLandingView(TemplateView):
    template_name = 'landing-page.html'


class InternationalLandingView(FormView):
    template_name = 'landing-page-international.html'
    success_template = 'landing-page-international-success.html'
    form_class = forms.InternationalBuyerForm

    def form_valid(self, form):
        data = forms.serialize_international_buyer_forms(form.cleaned_data)
        api_client.buyer.send_form(data)
        return TemplateResponse(self.request, self.success_template)


class EnrolmentInstructionsView(TemplateView):
    template_name = 'enrolment-instructions.html'

    def dispatch(self, request, *args, **kwargs):
        sso_user = request.sso_user
        if sso_user and helpers.user_has_verified_company(sso_user.id):
            return redirect('company-detail')
        return super().dispatch(request, *args, **kwargs)


class EnrolmentView(SSOLoginRequiredMixin, NamedUrlSessionWizardView):

    COMPANY = 'company-number'
    NAME = 'company-name'
    STATUS = 'exports'
    EMAIL = 'email'
    USER = 'mobile'
    SMS_VERIFY = 'mobile-verify'

    success_template = 'registered.html'
    failure_template = 'enrolment-error.html'
    form_list = (
        (COMPANY, forms.CompanyForm),
        (NAME, forms.CompanyNameForm),
        (STATUS, forms.CompanyExportStatusForm),
        (EMAIL, forms.CompanyEmailAddressForm),
        (USER, forms.UserForm),
        (SMS_VERIFY, forms.PhoneNumberVerificationForm),
    )
    templates = {
        COMPANY: 'company-form.html',
        NAME: 'company-form-name.html',
        STATUS: 'export-status-form.html',
        EMAIL: 'email-form.html',
        USER: 'user-form.html',
        SMS_VERIFY: 'sms-verify-form.html',
    }

    def dispatch(self, request, *args, **kwargs):
        if request.sso_user is None:
            return self.handle_no_permission()
        elif helpers.user_has_verified_company(request.sso_user.id):
            return redirect('company-detail')
        else:
            return super(EnrolmentView, self).dispatch(
                request, *args, **kwargs
            )

    def get_form_kwargs(self, step):
        if step == self.SMS_VERIFY:
            sms_code = helpers.get_sms_session_code(self.request.session)
            return {
                'encoded_sms_code': sms_code,
            }
        elif step == self.COMPANY:
            return {
                'session': self.request.session,
            }
        return {}

    def get_template_names(self):
        return [self.templates[self.steps.current]]

    def get_form_initial(self, step):
        if step == self.EMAIL:
            return forms.get_email_form_initial_data(
                email=self.request.sso_user.email
            )
        elif step == self.USER:
            referrer = self.request.session.get(constants.SESSION_KEY_REFERRER)
            return forms.get_user_form_initial_data(referrer=referrer)
        elif step == self.NAME:
            name = helpers.get_company_name_from_session(self.request.session)
            return forms.get_company_name_form_initial_data(name=name)

    def process_step(self, form):
        step = self.storage.current_step
        if step == self.USER:
            response = api_client.registration.send_verification_sms(
                phone_number=form.cleaned_data['mobile_number']
            )
            if not response.ok:
                response.raise_for_status()
            helpers.set_sms_session_code(
                session=self.request.session,
                sms_code=response.json()['sms_code']
            )
        return super().process_step(form)

    def serialize_form_data(self):
        data = forms.serialize_enrolment_forms(self.get_all_cleaned_data())
        date_of_creation = helpers.get_company_date_of_creation_from_session(
            self.request.session
        )
        data['sso_id'] = self.request.sso_user.id
        data['date_of_creation'] = date_of_creation
        return data

    def done(self, *args, **kwags):
        data = self.serialize_form_data()
        response = api_client.registration.send_form(data)
        if response.ok:
            template = self.success_template
        else:
            template = self.failure_template
        return TemplateResponse(self.request, template)


class CompanyEmailConfirmationView(View):
    failure_template = 'confirm-company-email-error.html'

    def get(self, request):
        code = request.GET.get('code')
        if code and api_client.registration.confirm_email(code):
            return redirect('company-detail')
        else:
            template = self.failure_template
        return TemplateResponse(request, template)


class UserCompanyBaseView(SSOLoginRequiredMixin):

    def dispatch(self, request, *args, **kwargs):
        if request.sso_user is None:
            return self.handle_no_permission()
        else:
            if not helpers.user_has_verified_company(self.request.sso_user.id):
                return redirect('register-instructions')
            else:
                return super(UserCompanyBaseView, self).dispatch(
                    request, *args, **kwargs
                )


class UpdateCompanyProfileOnFormWizardDoneMixin:

    def serialize_form_data(self):
        return self.form_serializer(self.get_all_cleaned_data())

    def done(self, *args, **kwargs):
        api_response = api_client.company.update_profile(
            sso_user_id=self.request.sso_user.id,
            data=self.serialize_form_data()
        )
        if api_response.ok:
            response = redirect('company-detail')
        else:
            response = TemplateResponse(self.request, self.failure_template)
        return response


class UserCompanyProfileEditView(
        UserCompanyBaseView,
        UpdateCompanyProfileOnFormWizardDoneMixin,
        SessionWizardView):

    form_list = (
        ('basic', forms.CompanyBasicInfoForm),
        ('size', forms.CompanySizeForm),
        ('classification', forms.CompanyClassificationForm),
    )
    failure_template = 'company-profile-update-error.html'
    templates = {
        'basic': 'company-profile-form.html',
        'size': 'company-profile-size-form.html',
        'classification': 'company-profile-form-classification.html',
    }
    form_serializer = staticmethod(forms.serialize_company_profile_forms)

    def get_form_initial(self, step):
        sso_user_id = self.request.sso_user.id
        response = api_client.company.retrieve_profile(sso_user_id)
        if not response.ok:
            response.raise_for_status()
        return response.json()

    def get_template_names(self):
        return [self.templates[self.steps.current]]


class UserCompanyProfileLogoEditView(
        UserCompanyBaseView,
        UpdateCompanyProfileOnFormWizardDoneMixin,
        SessionWizardView):

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
    form_serializer = staticmethod(forms.serialize_company_logo_forms)

    def get_template_names(self):
        return [self.templates[self.steps.current]]


class UserCompanyDescriptionEditView(
        UserCompanyBaseView,
        UpdateCompanyProfileOnFormWizardDoneMixin,
        SessionWizardView):

    form_list = (
        ('description', forms.CompanyDescriptionForm),
    )
    failure_template = 'company-profile-update-error.html'
    templates = {
        'description': 'company-profile-description-form.html',
    }
    form_serializer = staticmethod(forms.serialize_company_description_forms)

    def get_template_names(self):
        return [self.templates[self.steps.current]]

    def get_form_initial(self, step):
        sso_user_id = self.request.sso_user.id
        response = api_client.company.retrieve_profile(sso_user_id)
        if not response.ok:
            response.raise_for_status()
        return response.json()
