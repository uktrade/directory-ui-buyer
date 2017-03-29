from django.conf import settings
from django.http import HttpResponseForbidden

from proxy.views import BaseProxyView
from signature.utils import SignatureRejection


class CompanyPrivateAPIViewProxy(BaseProxyView):
    upstream = settings.API_CLIENT_BASE_URL

    def dispatch(self, request, *args, **kwargs):
        if SignatureRejection.test_signature(request) is False:
            return HttpResponseForbidden()
        return super().dispatch(request, path='', *args, **kwargs)
