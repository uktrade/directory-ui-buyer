import logging
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


api_client = DirectoryAPIClient(
    base_url=settings.API_CLIENT_BASE_URL,
    api_key=settings.API_CLIENT_API_KEY,
)

logger = logging.getLogger(__name__)


class CacheMixin(object):
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


class UpdateCompanyProfileOnFormWizardDoneMixin:
    def done(self, *args, **kwargs):
        session = self.request.user.session
        data = self.form_serializer(self.get_all_cleaned_data())
        if 'company_id' not in session:
            logger.error(
                'company_id is missing from the user session.',
                extra={'user_id': self.request.user.id}
            )
        company_id = session['company_id']
        response = api_client.company.update_profile(
            id=company_id, data=data
        )
        if response.ok:
            response = redirect('company-detail')
        else:
            response = TemplateResponse(self.request, self.failure_template)
        return response


class LandingView(CacheMixin, TemplateView):
    template_name = 'landing-page.html'


class EnrolmentView(UpdateCompanyProfileOnFormWizardDoneMixin,
                    SessionWizardView):
    success_template = 'registered.html'
    failure_template = 'enrolment-error.html'
    form_list = (
        ('company', forms.CompanyForm),
        ('name', forms.CompanyNameForm),
        ('status', forms.CompanyExportStatusForm),
        ('email', forms.CompanyEmailAddressForm),
        ('user', forms.UserForm),
    )
    templates = {
        'company': 'company-form.html',
        'name': 'company-form-name.html',
        'status': 'export-status-form.html',
        'email': 'email-form.html',
        'user': 'user-form.html',
    }

    def get_template_names(self):
        return [self.templates[self.steps.current]]

    def get_form_initial(self, step):
        if step == 'user':
            return {
                'referrer': self.request.session.get(SESSION_KEY_REFERRER)
            }
        if step == 'name':
            prev_data = self.storage.get_step_data('company') or {}
            number = prev_data.get('company-company_number')
            return {
                'company_name': helpers.get_company_name(number)
            }

    def done(self, *args, **kwags):
        data = forms.serialize_enrolment_forms(self.get_all_cleaned_data())
        response = api_client.registration.send_form(data)
        if response.ok:
            template = self.success_template
        else:
            template = self.failure_template
        return TemplateResponse(self.request, template)


class EmailConfirmationView(View):
    success_template = 'confirm-email-success.html'
    failure_template = 'confirm-email-error.html'

    def get(self, request):
        code = request.GET.get('confirmation_code')
        if code and api_client.registration.confirm_email(code):
            template = self.success_template
        else:
            template = self.failure_template
        return TemplateResponse(request, template)


class CompanyProfileDetailView(TemplateView):
    template_name = 'company-profile-details.html'

    def get_context_data(self, **kwargs):
        # once login has been implemented company_id will be added to
        # the user's session automatically after the user logs in.
        session = self.request.user.session
        if 'company_id' not in session:
            logger.error(
                'company_id is missing from the user session.',
                extra={'user_id': self.request.user.id}
            )
        company_id = session['company_id']
        company_details = api_client.company.retrieve_profile(id=company_id)
        return {
            'company': {
                'website': company_details['website'],
                'description': company_details['description'],
                'number': company_details['number'],
                'sectors': company_details['sectors'],
                'logo': company_details['logo'],
            }
        }


class CompanyProfileEditView(UpdateCompanyProfileOnFormWizardDoneMixin,
                             SessionWizardView):
    form_list = (
        ('basic', forms.CompanyBasicInfoForm),
        ('size', forms.CompanySizeForm),
        ('classification', forms.CompanyClassificationForm),
    )
    failure_template = 'company-profile-update-error.html'
    templates = {
        'basic': 'company-profile-form.html',
        'size': 'company-profile-form.html',
        'classification': 'company-profile-form-classification.html',
    }
    form_serializer = forms.serialize_company_profile_forms

    def get_template_names(self):
        return [self.templates[self.steps.current]]


class CompanyProfileLogoEditView(UpdateCompanyProfileOnFormWizardDoneMixin,
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
    form_serializer = forms.serialize_company_logo_forms

    def get_template_names(self):
        return [self.templates[self.steps.current]]


class CompanyDescriptionEditView(UpdateCompanyProfileOnFormWizardDoneMixin,
                                 SessionWizardView):
    form_list = (
        ('description', forms.CompanyDescriptionForm),
    )
    failure_template = 'company-profile-update-error.html'
    templates = {
        'description': 'company-profile-description-form.html',
    }
    form_serializer = forms.serialize_company_description_forms

    def get_template_names(self):
        return [self.templates[self.steps.current]]
