from django.utils import translation
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from directory_components.middleware import AbstractPrefixUrlMiddleware


class PrefixUrlMiddleware(AbstractPrefixUrlMiddleware):
    prefix = '/find-a-buyer/'


class GA360Middleware(MiddlewareMixin):

    def process_template_response(self, request, response):

        ga360_payload = {
            'page_id': '',
            'business_unit': settings.GA360_BUSINESS_UNIT,
            'site_language': translation.get_language(),
            'site_section': settings.GA360_SITE_SECTION,
            'site_subsection': '',
        }

        if request.user.is_authenticated:
            ga360_payload['user_id'] = str(request.user.hashed_uuid)
            ga360_payload['login_status'] = True
        else:
            ga360_payload['user_id'] = None
            ga360_payload['login_status'] = False

        response.context_data = response.context_data or {}
        response.context_data['ga360'] = ga360_payload
        return response
