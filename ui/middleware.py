import sys

from urllib.parse import urlsplit, urlunsplit
from django.http import HttpResponseRedirect

from ui import helpers
from ui.constants import SESSION_KEY_REFERRER


class SSLRedirectMiddleware:

    def process_request(self, request):
        if not request.is_secure():
            if "runserver" not in sys.argv and "test" not in sys.argv:
                return HttpResponseRedirect(urlunsplit(
                    ["https"] + list(urlsplit(request.get_raw_uri())[1:])))


class ReferrerMiddleware(object):
    def process_request(self, request):
        referrer = helpers.get_referrer_from_request(request)
        if referrer:
            request.session[SESSION_KEY_REFERRER] = referrer
