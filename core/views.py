from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView

from core.pingdom.services import health_check_services

HEALTH_CHECK_STATUS = 0
HEALTH_CHECK_EXCEPTION = 1


class PingDomView(TemplateView):
    template_name = 'directory_healthcheck/pingdom.xml'

    status = 'OK'

    @method_decorator(never_cache)
    def get(self, *args, **kwargs):

        checked = {}
        for service in health_check_services:
            checked[service.name] = service().check()

        if all(item[HEALTH_CHECK_STATUS] for item in checked.values()):
            return HttpResponse(
                render_to_string(self.template_name, {'status': self.status, 'errors': []}),
                status=200,
                content_type='text/xml',
            )
        else:
            self.status = 'FALSE'
            errors = []
            for service_result in filter(lambda x: x[HEALTH_CHECK_STATUS] is False, checked.values()):
                errors.append(service_result[HEALTH_CHECK_EXCEPTION])
            return HttpResponse(
                render_to_string(self.template_name, {'status': self.status, 'errors': errors}),
                status=500,
                content_type='text/xml',
            )
