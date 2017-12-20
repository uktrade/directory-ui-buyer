from directory_healthcheck.views import BaseHealthCheckAPIView

from healthcheck.backends import APIBackend, SigngleSignOnBackend


class APICheckAPIView(BaseHealthCheckAPIView):
    def create_service_checker(self):
        return APIBackend()


class SingleSignOnAPIView(BaseHealthCheckAPIView):
    def create_service_checker(self):
        return SigngleSignOnBackend()
