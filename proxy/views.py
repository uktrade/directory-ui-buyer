import urllib3

from django.conf import settings
from django.shortcuts import redirect

from revproxy.response import get_django_response
from revproxy.views import ProxyView
from ui import signature


class BaseProxyView(ProxyView):
    upstream = settings.API_CLIENT_BASE_URL
    set_forwarded_host_header = True

    def __init__(self, *args, **kwargs):
        if self.upstream.endswith('/'):
            self.upstream = self.upstream[:-1]

        super(BaseProxyView, self).__init__(*args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        self.request_headers = self.get_request_headers()

        redirect_to = self._format_path_to_redirect(request)
        if redirect_to:
            return redirect(redirect_to)

        upstream_response = self.get_upstream_response(request)

        self._replace_host_on_redirect_location(request, upstream_response)
        self._set_content_type(request, upstream_response)

        response = get_django_response(upstream_response)

        self.log.debug("Response returned: %s", response)

        return response

    def get_signature_header(self, url, body):
        return signature.api_signer.get_signature_headers(url=url, body=body)

    def get_upstream(self):
        return super(BaseProxyView, self).get_upstream(path=None)

    def get_upstream_response(self, request, *args, **kwargs):
        request_payload = request.body

        self.log.debug("Request headers: %s", self.request_headers)

        request_url = self.get_upstream() + request.get_full_path()

        self.log.debug("Request URL: %s", request_url)

        signature_headers = self.get_signature_header(
            url=request_url, body=request_payload
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
