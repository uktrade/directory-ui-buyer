from django.conf import settings
from django.http import HttpResponseForbidden

from proxy.views import BaseProxyView
from signature.utils import SignatureRejection


class CompanyPrivateAPIViewProxy(BaseProxyView):
    upstream = settings.API_CLIENT_BASE_URL
    # setting forwarded_host header cause image returned to use FAB's domain
    set_forwarded_host_header = False

    def dispatch(self, request, *args, **kwargs):
        if SignatureRejection.test_signature(request) is False:
            return HttpResponseForbidden()
        return super().dispatch(request, path='', *args, **kwargs)
