import json

from django.conf import settings
from django.shortcuts import redirect
from django.views.generic import TemplateView

from alice.helpers import rabbit


class IndexView(TemplateView):
    template_name = "index.html"

    def post(self, request):
        r = request.POST
        json_data = {'data': json.dumps(r)}
        response = rabbit.post(
            settings.DATA_SERVER + '/form/',
            data=json_data,
            request=self.request,
        )

        if not response.status_code == 201:
            raise Exception(response.content)

        return redirect("thanks")
