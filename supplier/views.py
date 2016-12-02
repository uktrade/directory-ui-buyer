from directory_api_client.client import DirectoryAPIClient

from django.conf import settings
from django.views.generic import TemplateView

from sso.utils import SSOLoginRequiredMixin


api_client = DirectoryAPIClient(
    base_url=settings.API_CLIENT_BASE_URL,
    api_key=settings.API_CLIENT_KEY,
)


class SupplierProfileDetailView(SSOLoginRequiredMixin, TemplateView):
    template_name = 'supplier-profile-details.html'

    def get_context_data(self, **kwargs):
        supplier_details = api_client.supplier.retrieve_profile(
            sso_id=self.request.sso_user.id
        )
        return {
            'supplier': {
                'company_email': supplier_details['company_email'],
                'mobile_number': supplier_details['mobile_number'],
                'company_id': supplier_details['company_id'],
            }
        }
