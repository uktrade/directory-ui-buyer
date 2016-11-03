import logging
import json
import os

from directory_api_client.client import DirectoryAPIClient
from formtools.wizard.views import SessionWizardView

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.cache import patch_response_headers
from django.views.generic import TemplateView
from django.views.generic.base import View

from enrolment import forms, helpers
from enrolment.constants import SESSION_KEY_REFERRER
from sso.utils import SSOLoginRequiredMixin


api_client = DirectoryAPIClient(
    base_url=settings.API_CLIENT_BASE_URL,
    api_key=settings.API_CLIENT_KEY,
)

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


class LandingView(CacheMixin, TemplateView):
    domestic_template_name = 'landing-page.html'
    international_template_name = 'landing-page-international.html'

    def get_template_names(self):
        if helpers.is_request_international(self.request):
            return [self.international_template_name]
        else:
            return [self.domestic_template_name]


class EnrolmentView(SSOLoginRequiredMixin, SessionWizardView):

    success_template = 'registered.html'
    failure_template = 'enrolment-error.html'
    form_list = (
        ('company', forms.CompanyForm),
        ('name', forms.CompanyNameForm),
        ('status', forms.CompanyExportStatusForm),
        ('email', forms.CompanyEmailAddressForm),
        ('user', forms.UserForm),
        ('sms_verify', forms.PhoneNumberVerificationForm),
    )
    templates = {
        'company': 'company-form.html',
        'name': 'company-form-name.html',
        'status': 'export-status-form.html',
        'email': 'email-form.html',
        'user': 'user-form.html',
        'sms_verify': 'sms-verify-form.html'
    }

    def dispatch(self, request, *args, **kwargs):
        if request.sso_user is None:
            return self.handle_no_permission()
        elif helpers.user_has_company(sso_user_id=request.sso_user.id):
            return redirect('company-detail')
        else:
            return super(EnrolmentView, self).dispatch(
                request, *args, **kwargs
            )

    def get_form_kwargs(self, step):
        if step == 'sms_verify':
            return {
                'expected_sms_code': str(self.request.session.get('sms_code')),
            }
        return {}

    def get_template_names(self):
        return [self.templates[self.steps.current]]

    def get_form_initial(self, step):
        if step == 'user':
            return {
                'referrer': self.request.session.get(SESSION_KEY_REFERRER)
            }
        if step == 'name':
            prev_data = self.storage.get_step_data('company') or {}
            company_number = prev_data.get('company-company_number')
            return {
                'company_name': helpers.get_company_name(company_number)
            }

    def process_step(self, form):
        step = self.storage.current_step
        if step == 'user':
            response = api_client.registration.send_verification_sms(
                phone_number=form.cleaned_data['mobile_number']
            )
            if not response.ok:
                response.raise_for_status()
            # TODO: change session backend to no longer be cookie based
            # because we're sharing secrets here
            self.request.session['sms_code'] = response.json()['sms_code']
        return super().process_step(form)

    def done(self, *args, **kwags):
        data = forms.serialize_enrolment_forms(self.get_all_cleaned_data())
        data['sso_id'] = self.request.sso_user.id
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
            if not helpers.user_has_company(self.request.sso_user.id):
                return redirect('register')
            else:
                return super(UserCompanyBaseView, self).dispatch(
                    request, *args, **kwargs
                )


class UserCompanyProfileDetailView(UserCompanyBaseView, TemplateView):
    template_name = 'company-profile-details.html'

    def get_context_data(self, **kwargs):
        response = api_client.company.retrieve_profile(
            sso_user_id=self.request.sso_user.id
        )
        if not response.ok:
            response.raise_for_status()
        details = response.json()
        sectors = json.loads(details['sectors']) if details['sectors'] else []
        return {
            'company': {
                'website': details['website'],
                'description': details['description'],
                'number': details['number'],
                'sectors': helpers.get_sectors_labels(sectors),
                'logo': details['logo'],
                'name': details['name'],
                'keywords': details['keywords'],
                'employees': helpers.get_employees_label(details['employees']),
            }
        }


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
