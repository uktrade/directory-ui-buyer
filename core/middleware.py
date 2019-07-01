from django.utils import translation
from django.conf import settings

from directory_components.middleware import AbstractPrefixUrlMiddleware


class PrefixUrlMiddleware(AbstractPrefixUrlMiddleware):
    prefix = '/find-a-buyer/'


class AddDefaultGAValuesMiddleware:

    def process_template_response(self, request, response):

        ga360_payload = {
            'page_id': '',
            'business_unit': settings.GA360_BUSINESS_UNIT,
            'site_language': translation.get_language(),
            'site_section': settings.GA360_SITE_SECTION,
            'site_subsection': '',
        }

        try:
            ga360_payload['user_id'] = str(request.sso_user.id)
            ga360_payload['login_status'] = True

        except AttributeError:
            ga360_payload['user_id'] = None
            ga360_payload['login_status'] = False

        response.context_data['ga360'] = ga360_payload
        return response
