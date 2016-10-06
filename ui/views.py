from formtools.wizard.views import SessionWizardView

from django.template.response import TemplateResponse
from django.utils.cache import patch_response_headers
from django.views.generic import TemplateView
from django.views.generic.base import View

from ui import forms
from ui.clients.directory_api import api_client


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


class RegistrationView(SessionWizardView):
    form_list = (
        forms.CompanyForm,
        forms.AimsForm,
        forms.UserForm,
    )

    def get_template_names(self):
        return [
            'company-form.html',
            'aims-form.html',
            'user-form.html',
        ]

    def done(self, form_list, form_dict):
        return TemplateResponse(self.request, 'registered.html')


class EmailConfirmationView(View):
    success_template = 'confirm-email-success.html'
    failure_template = 'confirm-email-error.html'

    def get(self, request):
        confirmation_code = request.GET.get('confirmation_code')
        if confirmation_code and api_client.confirm_email(confirmation_code):
            template = self.success_template
        else:
            template = self.failure_template
        return TemplateResponse(request, template)
