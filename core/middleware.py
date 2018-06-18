from django.conf import settings
from django.shortcuts import redirect


class MaintenanceModeMiddleware:
    maintenance_url = 'https://sorry.great.gov.uk'

    def process_request(self, request):
        if settings.FEATURE_MAINTENANCE_MODE_ENABLED:
            return redirect(self.maintenance_url)
