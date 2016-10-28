import http

from directory_api_client.client import DirectoryAPIClient
from formtools.wizard.views import SessionWizardView

from django.conf import settings
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views.generic import TemplateView

from sso.utils import SSOLoginRequiredMixin
from user import forms


api_client = DirectoryAPIClient(
    base_url=settings.API_CLIENT_BASE_URL,
    api_key=settings.API_CLIENT_KEY,
)


class UserProfileDetailView(SSOLoginRequiredMixin, TemplateView):
    template_name = 'user-profile-details.html'

    def get_context_data(self, **kwargs):
        user_details = api_client.user.retrieve_profile(
            sso_id=self.request.sso_user.id
        )
        return {
            'user': {
                'company_email': user_details['company_email'],
                'mobile_number': user_details['mobile_number'],
                'company_id': user_details['company_id'],
            }
        }


class UserProfileEditView(SSOLoginRequiredMixin, SessionWizardView):
    form_list = (
        ('basic_info', forms.UserBasicInfoForm),
    )
    failure_template = 'user-profile-update-error.html'

    def get_template_names(self):
        return [
            'user-profile-edit-form.html',
        ]

    def done(self, *args, **kwargs):
        data = forms.serialize_user_profile_forms(
            self.get_all_cleaned_data()
        )
        response = api_client.user.update_profile(
            sso_id=self.request.sso_user.id,
            data=data
        )
        if response.status_code == http.client.OK:
            response = redirect('user-detail')
        else:
            response = TemplateResponse(self.request, self.failure_template)
        return response
