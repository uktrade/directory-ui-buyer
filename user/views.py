from django.views.generic import TemplateView

from registration.clients.directory_api import api_client


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
