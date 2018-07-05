import urllib3

from django.conf import settings
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, Http404

from revproxy.response import get_django_response
from revproxy.views import ProxyView

from conf import signature


class BaseProxyView(ProxyView):
    upstream = settings.API_CLIENT_BASE_URL
    set_forwarded_host_header = True

    def __init__(self, *args, **kwargs):
        if self.upstream.endswith('/'):
            self.upstream = self.upstream[:-1]

        super(BaseProxyView, self).__init__(*args, **kwargs)

    def dispatch(self, request, path=None, *args, **kwargs):
        path = path or request.get_full_path()
        self.request_headers = self.get_request_headers()

        redirect_to = self._format_path_to_redirect(request)
        if redirect_to:
            return redirect(redirect_to)

        upstream_response = self.get_upstream_response(request, path)

        self._replace_host_on_redirect_location(request, upstream_response)
        self._set_content_type(request, upstream_response)

        response = get_django_response(upstream_response)

        self.log.debug("Response returned: %s", response)

        return response

    def get_upstream(self):
        return super(BaseProxyView, self).get_upstream(path=None)

    def get_upstream_response(self, request, path, *args, **kwargs):
        request_payload = request.body

        self.log.debug("Request headers: %s", self.request_headers)

        request_url = self.get_upstream() + path

        self.log.debug("Request URL: %s", request_url)

        signature_headers = signature.api_signer.get_signature_headers(
            url=request_url,
            body=request_payload,
            method=request.method,
            content_type=self.request_headers.get('Content-Type'),
        )
        if self.set_forwarded_host_header:
            self.request_headers["X-Forwarded-Host"] = request.get_host()
        self.request_headers = {**self.request_headers, **signature_headers}

        try:
            upstream_response = self.http.urlopen(
                request.method,
                request_url,
                redirect=False,
                retries=self.retries,
                headers=self.request_headers,
                body=request_payload,
                decode_content=False,
                preload_content=False
            )
            self.log.debug(
                "Proxy response header: %s",
                upstream_response.getheaders()
            )
        except urllib3.exceptions.HTTPError as error:
            self.log.exception(error)
            raise
        else:
            return upstream_response


class APIViewProxy(BaseProxyView):
    upstream = settings.API_CLIENT_BASE_URL
    # setting forwarded_host header cause image returned to use FAB's domain
    set_forwarded_host_header = False

    def dispatch(self, request, path, *args, **kwargs):
        if signature.external_api_checker.test_signature(request) is False:
            return HttpResponseForbidden()
        return super().dispatch(request, path, *args, **kwargs)


class DirectoryAPIViewProxy(APIViewProxy):

    def dispatch(self, *args, **kwargs):
        if not settings.EXPOSE_DIRECTORY_API:
            raise Http404()
        return super().dispatch(*args, **kwargs)
