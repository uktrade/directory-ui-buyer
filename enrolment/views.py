import logging

from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views.generic import FormView, View
from django.forms import ValidationError
from django.shortcuts import render

from formtools.wizard.views import NamedUrlSessionWizardView

from directory_api_client.client import api_client
from enrolment import forms, helpers
from enrolment.helpers import (
    store_companies_house_profile_in_session_and_validate
)
from sso.utils import SSOSignUpRequiredMixin

COMPANY_NUMBER_NOT_PROVIDED_ERROR = 'Company number not provided.'
EXPORT_STATUS_NOT_PROVIDED_ERROR = 'Export status not provided.'

logger = logging.getLogger(__name__)


class DomesticLandingView(FormView):
    template_name = 'landing-page.html'
    form_class = forms.CompanyNumberForm
    http_method_names = ['get', 'post']

    def dispatch(self, request, *args, **kwargs):
        user = request.sso_user
        if user and helpers.has_company(user.session_id):
            return redirect('company-detail')
        else:
            return super(DomesticLandingView, self).dispatch(
                request, *args, **kwargs
            )

    def form_valid(self, form):

        url = '{path}?company_number={number}'.format(
            path=reverse('register',  kwargs={'step': 'company'}),
            number=form.cleaned_data['company_number']
        )
        return HttpResponseRedirect(url)

    @staticmethod
    def get_supplier_profile_url(number):
        return settings.SUPPLIER_PROFILE_URL.format(number=number)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.sso_user
        context['user_has_company'] = (
            user and helpers.has_company(user.session_id)
        )
        context['supplier_profile_urls'] = {
            'immersive': self.get_supplier_profile_url('07723438'),
            'blippar': self.get_supplier_profile_url('07446749'),
            'briggs': self.get_supplier_profile_url('06836628'),
        }

        return context


class EnrolmentView(NamedUrlSessionWizardView):

    COMPANY = 'company'

    form_list = (
        (COMPANY, forms.CompanyForm),
    )
    templates = {
        COMPANY: 'company-form.html',
    }
    form_labels = (
        (COMPANY, 'Confirm company'),
    )

    def dispatch(self, request, *args, **kwargs):
        user = request.sso_user
        if user and helpers.has_company(user.session_id):
            return redirect('company-detail')
        else:
            return super(EnrolmentView, self).dispatch(
                request, *args, **kwargs
            )

    def get_template_names(self):
        return [self.templates[self.steps.current]]

    def get_requested_number(self):
        company_number = (
            self.request.GET.get('company_number') or
            helpers.get_company_number_from_session(self.request.session)
        )
        if not company_number:
            raise ValidationError(COMPANY_NUMBER_NOT_PROVIDED_ERROR)
        else:
            return company_number

    def get(self, *args, **kwargs):
        stored_number = helpers.get_company_number_from_session(
            self.request.session
        )
        if kwargs.get('step') == self.COMPANY:
            try:
                requested_number = self.get_requested_number()
                if stored_number != requested_number:
                    # If the user already performed company lookup and went
                    # back to landing page to request a different company
                    # we need to reset form wizard storage and update session
                    self.storage.reset()
                    store_companies_house_profile_in_session_and_validate(
                        session=self.request.session,
                        company_number=requested_number
                    )
            except ValidationError as error:
                context = {'validation_error': error.message}
                return helpers.get_error_response(self.request, context)
        return super().get(*args, **kwargs)

    def get_form_initial(self, step):
        if step == self.COMPANY:
            return forms.get_company_form_initial_data(
                data=helpers.get_company_from_session(self.request.session)
            )

    def done(self, *args, **kwargs):
        company_number = helpers.get_company_number_from_session(
            self.request.session
        )
        url = '{path}?company_number={number}'.format(
            path=reverse('register-submit'),
            number=company_number,
        )
        return HttpResponseRedirect(url)

    def get_context_data(self, form,  *args, **kwargs):
        context = super().get_context_data(
            form=form, form_labels=self.form_labels, *args, **kwargs
        )
        if self.steps.current == self.COMPANY:
            context.update(form.initial)
        return context


class SubmitEnrolmentView(SSOSignUpRequiredMixin, View):
    failure_template = 'enrolment-failed.html'

    def dispatch(self, request, *args, **kwargs):
        if request.sso_user is None:
            return self.handle_no_permission()
        elif helpers.has_company(request.sso_user.session_id):
            return redirect('company-detail')
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_enrolment_data(self):
        session = self.request.session
        date_of_creation = helpers.get_date_of_creation_from_session(session)
        address = helpers.get_company_address_from_session(session)
        return {
            'sso_id': self.request.sso_user.id,
            'company_email': self.request.sso_user.email,
            'contact_email_address': self.request.sso_user.email,
            'company_number': helpers.get_company_number_from_session(session),
            'date_of_creation': date_of_creation,
            'company_name': helpers.get_company_name_from_session(session),
            'address_line_1': address.get('address_line_1', ''),
            'address_line_2': address.get('address_line_2', ''),
            'locality': address.get('locality', ''),
            'country': address.get('country', ''),
            'postal_code': address.get('postal_code', ''),
            'po_box': address.get('po_box', ''),
        }

    def get_company_number(self):
        company_number = self.request.GET.get('company_number')
        if not company_number:
            raise ValidationError(COMPANY_NUMBER_NOT_PROVIDED_ERROR)
        else:
            return company_number

    def get(self, request, *args, **kwargs):
        try:
            helpers.store_companies_house_profile_in_session_and_validate(
                session=self.request.session,
                company_number=self.get_company_number()
            )
        except ValidationError as error:
            context = {'validation_error': error.message}
            return render(request, 'enrolment-error.html', context)

        data = self.get_enrolment_data()
        api_response = api_client.enrolment.send_form(data)
        if not api_response.ok:
            logger.error(
                "Enrolment failed, API response: {}".format(
                    api_response.content
                )
            )
            response = TemplateResponse(self.request, self.failure_template)
        else:
            response = redirect('company-edit')
        return response


class CompaniesHouseSearchApiView(View):
    form_class = forms.CompaniesHouseSearchForm

    def get(self, request, *args, **kwargs):
        form = self.form_class(data=request.GET)
        if not form.is_valid():
            return JsonResponse(form.errors, status=400)
        api_response = helpers.CompaniesHouseClient.search(
            term=form.cleaned_data['term']
        )
        api_response.raise_for_status()
        return JsonResponse(api_response.json()['items'], safe=False)
