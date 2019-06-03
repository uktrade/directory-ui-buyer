from django.shortcuts import redirect
from django.views.generic import TemplateView

from directory_constants import urls
from enrolment import helpers


class DomesticLandingView(TemplateView):
    template_name = 'landing-page.html'

    def dispatch(self, request, *args, **kwargs):
        user = request.sso_user
        if user and helpers.has_company(user.session_id):
            return redirect('company-detail')
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            enrolment_url=urls.build_great_url('profile/enrol')
        )
