from django.conf import settings
from django.shortcuts import redirect
from django.views.generic import TemplateView

from directory_constants import urls


class DomesticLandingView(TemplateView):
    template_name = 'landing-page.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.company:
            return redirect('company-detail')
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        if self.request.user.is_authenticated:
            enrolment_url = urls.build_great_url('profile/enrol')
        else:
            enrolment_url = settings.SSO_PROXY_LOGIN_URL
        return super().get_context_data(
            **kwargs,
            enrolment_url=enrolment_url
        )
