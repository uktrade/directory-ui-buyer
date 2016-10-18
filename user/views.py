import http

from formtools.wizard.views import SessionWizardView

from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views.generic import TemplateView

from enrolment.clients.directory_api import api_client
from user import forms


class UserProfileDetailView(TemplateView):
    template_name = 'user-profile-details.html'

    def get_context_data(self, **kwargs):
        user_id = self.request.user.id
        user_details = api_client.user.retrieve_profile(id=user_id)
        return {
            'user': {
                'name': user_details['name'],
                'email': user_details['email'],
            }
        }


class UserProfileEditView(SessionWizardView):
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
        response = api_client.user.update_profile(data)
        if response.status_code == http.client.OK:
            response = redirect('user-detail')
        else:
            response = TemplateResponse(self.request, self.failure_template)
        return response
