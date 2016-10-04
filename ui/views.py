import json
import os

from formtools.wizard.views import SessionWizardView

from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import render, redirect
from django.template.response import TemplateResponse
from django.utils.cache import patch_response_headers
from django.views.generic import TemplateView, FormView

from alice.helpers import rabbit
from ui import forms


class CacheMixin(object):
    def render_to_response(self, context, **response_kwargs):
        # Get response from parent TemplateView class
        response = super().render_to_response(
            context, **response_kwargs
        )

        # Add Cache-Control and Expires headers
        patch_response_headers(response, cache_timeout=60 * 30)

        # Return response
        return response


class CachableTemplateView(CacheMixin, TemplateView):
    pass


class IndexView(CacheMixin, FormView):
    template_name = "index.html"
    form_class = forms.ContactForm
    success_url = reverse_lazy("thanks")

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        json_data = {'data': json.dumps(form.cleaned_data)}
        response = rabbit.post(
            settings.DATA_SERVER + '/form/',
            data=json_data,
            request=self.request,
        )

        if not response.ok:
            return redirect("problem")

        return super().form_valid(form)


class RegisterView(SessionWizardView):
    form_list = (
        forms.CompanyForm,
        forms.PasswordForm,
    )

    def get_template_names(self):
        return ['step1.html', 'step2.html']

    def done(self, form_list, form_dict):
        return render(self.request, 'registered.html')
