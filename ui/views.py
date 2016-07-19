import json

from django.conf import settings
from django.shortcuts import redirect
from django.core.urlresolvers import reverse_lazy
from django.views.generic import TemplateView, FormView

from alice.helpers import rabbit
from ui.forms import ContactForm


class IndexView(FormView):
    template_name = "index.html"
    form_class = ContactForm
    success_url = reverse_lazy("thanks")

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.

        r = self.request.POST
        json_data = {'data': json.dumps(r)}
        response = rabbit.post(
            settings.DATA_SERVER + '/form/',
            data=json_data,
            request=self.request,
        )

        if not response.status_code == 201:
            return redirect("problem")

        return super().form_valid(form)
