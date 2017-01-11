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
        if not self.has_sso_user():
            return self.handle_no_permission()
        return super(SSOLoginRequiredMixin, self).dispatch(
            request, *args, **kwargs
        )

    def handle_no_permission(self):
        return HttpResponseRedirect(self.get_login_url())

    def has_sso_user(self):
        return self.request.sso_user is not None

    def get_login_url(self):
        """
        Returns a url, adding the 'next' url to the querystring

        """

        resolved_url = resolve_url(settings.SSO_LOGIN_URL)
        next_url = self.request.build_absolute_uri()
        login_url_parts = list(urlparse(resolved_url))
        querystring = QueryDict(login_url_parts[4], mutable=True)
        querystring[settings.SSO_REDIRECT_FIELD_NAME] = next_url
        login_url_parts[4] = querystring.urlencode(safe='/')

        return urlunparse(login_url_parts)
