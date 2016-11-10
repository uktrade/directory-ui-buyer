from directory_api_client.client import DirectoryAPIClient

from django.conf import settings
from django.views.generic import TemplateView

from sso.utils import SSOLoginRequiredMixin

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
