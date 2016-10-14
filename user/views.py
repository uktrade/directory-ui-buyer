from django.views.generic import TemplateView

from registration.clients.directory_api import api_client


class UserProfileDetailView(TemplateView):
    template_name = 'user-profile-details.html'

    def get_context_data(self, **kwargs):
        # TODO: ED-183
        # Determine the user_id of the logged in user.
        user_id = 1
        user_details = api_client.user.retrieve_profile(id=user_id)
        return {
            'user': {
                'name': user_details['name'],
                'email': user_details['email'],
            }
        }
