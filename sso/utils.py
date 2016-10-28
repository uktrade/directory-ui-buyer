from django.conf import settings
from django.http import HttpResponseRedirect, QueryDict
from django.utils.six.moves.urllib.parse import urlparse, urlunparse
from django.shortcuts import resolve_url

from directory_sso_api_client.client import DirectorySSOAPIClient


sso_api_client = DirectorySSOAPIClient(
    base_url=settings.SSO_API_CLIENT_BASE_URL,
    api_key=settings.SSO_API_CLIENT_KEY,
)


class SSOUser:

    def __init__(self, id, email):
        self.id = id
        self.email = email


class SSOLoginRequiredMixin:
    """ CBV mixin which verifies sso user """

    def dispatch(self, request, *args, **kwargs):
        if request.sso_user is None:
            return self.handle_no_permission()
        return super(SSOLoginRequiredMixin, self).dispatch(
            request, *args, **kwargs
        )

    def handle_no_permission(self):
        return self.redirect_to_login(
            next_url=self.request.build_absolute_uri(),
        )

    def redirect_to_login(self, next_url):
        """
        Redirects the user to the sso login page, passing the given 'next' page
        """
        resolved_url = resolve_url(settings.SSO_LOGIN_URL)
        login_url_parts = list(urlparse(resolved_url))
        querystring = QueryDict(login_url_parts[4], mutable=True)
        querystring[settings.SSO_REDIRECT_FIELD_NAME] = next_url
        login_url_parts[4] = querystring.urlencode(safe='/')

        return HttpResponseRedirect(urlunparse(login_url_parts))
