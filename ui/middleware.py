from django.conf import settings


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
        if request.sso_user:
            response['Cache-Control'] = 'no-store, no-cache'
        return response
