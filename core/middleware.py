from django.conf import settings
from django.shortcuts import redirect


class MaintenanceModeMiddleware:
    maintenance_url = 'https://sorry.great.gov.uk'

    def process_request(self, request):
        if settings.FEATURE_MAINTENANCE_MODE_ENABLED:
            return redirect(self.maintenance_url)


class NoCacheMiddlware:
    """Tell the browser to not cache the pages.

    Information that should be kept private can be viewed by anyone
    with access to the files in the browser's cache directory.

    """

    def __init__(self, *args, **kwargs):
        # `NoCacheMiddlware` depends on `request.sso_user`, which comes from
        # `SSOUserMiddleware
        assert (
            'sso.middleware.SSOUserMiddleware' in settings.MIDDLEWARE_CLASSES
        )
        super().__init__(*args, **kwargs)

    def process_response(self, request, response):
        if getattr(request, 'sso_user', None):
            response['Cache-Control'] = 'no-store, no-cache'
        return response
