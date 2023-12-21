from urllib.parse import quote

from directory_constants import urls
from directory_components.helpers import add_next

from django.conf import settings
from django.shortcuts import redirect
from django.views.generic import TemplateView


class DomesticLandingView(TemplateView):
    template_name = 'landing-page.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.company:
            return redirect('company-detail')
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        enrolment_url = (urls.domestic.SINGLE_SIGN_ON_PROFILE / 'enrol/') + '?business-profile-intent=true'
        if not self.request.user.is_authenticated:
            enrolment_url = add_next(
                destination_url=settings.SSO_PROXY_LOGIN_URL,
                current_url=quote(enrolment_url)
            )
        return super().get_context_data(
            **kwargs,
            enrolment_url=enrolment_url
        )
