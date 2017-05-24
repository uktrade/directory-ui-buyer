import http

from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import JsonResponse, Http404, HttpResponseRedirect
from django.shortcuts import redirect
from django.template.response import TemplateResponse, SimpleTemplateResponse
from django.views.generic import FormView, TemplateView, View
from django.forms import ValidationError

from formtools.wizard.views import NamedUrlSessionWizardView
import requests

from api_client import api_client
from enrolment import forms, helpers, validators
from sso.utils import SSOLoginRequiredMixin


class DomesticLandingView(FormView):
    template_name = 'landing-page.html'
    form_class = forms.CompanyNumberForm
    http_method_names = ['get', 'post']

    def get_template_names(self):
        if settings.NEW_LANDING_PAGE_FEATURE_ENABLED:
            return [self.template_name]
        return ['landing-page-old.html']

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

        context['user_has_company'] = (
            self.request.sso_user and helpers.has_company(
                self.request.sso_user.id
            )
        )
        context['supplier_profile_urls'] = {
            'immersive': self.get_supplier_profile_url('07723438'),
            'blippar': self.get_supplier_profile_url('07446749'),
            'briggs': self.get_supplier_profile_url('06836628'),
        }
        context['buyers_waiting_number'] = settings.BUYERS_WAITING_NUMBER

        return context


class EnrolmentInstructionsView(TemplateView):
    template_name = 'enrolment-instructions.html'

    def dispatch(self, request, *args, **kwargs):
        sso_user = request.sso_user
        if sso_user and helpers.has_company(sso_user.id):
            return redirect('company-detail')
        return super().dispatch(request, *args, **kwargs)


class EnrolmentView(SSOLoginRequiredMixin, NamedUrlSessionWizardView):

    COMPANY = 'company'
    STATUS = 'exports'

    success_template = 'registered.html'
    failure_template = 'enrolment-error.html'
    form_list = (
        (COMPANY, forms.CompanyForm),
        (STATUS, forms.CompanyExportStatusForm),
    )
    templates = {
        COMPANY: 'company-form.html',
        STATUS: 'export-status-form.html',
    }
    form_labels = (
        (COMPANY, 'Confirm company'),
        (STATUS, 'Export status'),
    )

    def dispatch(self, request, *args, **kwargs):
        if request.sso_user is None:
            return self.handle_no_permission()
        elif helpers.has_company(request.sso_user.id):
            return redirect('company-detail')
        else:
            return super(EnrolmentView, self).dispatch(
                request, *args, **kwargs
            )

    def get_template_names(self):
        return [self.templates[self.steps.current]]

    @staticmethod
    def store_companies_house_profile_in_session_and_validate(
            session, company_number
    ):
        try:
            helpers.store_companies_house_profile_in_session(
                session=session,
                company_number=company_number,
            )
        except requests.exceptions.RequestException as error:
            if error.response.status_code == http.client.NOT_FOUND:
                raise ValidationError(
                    'Company not found. Please check the number.'
                )
            else:
                raise ValidationError(
                    'Error. Please try again later.'
                )
        else:
            company_status = helpers.get_company_status_from_session(
                session
            )
            validators.company_active(company_status)
            validators.company_unique(company_status)

    def get(self, *args, **kwargs):
        step_url = kwargs.get('step', None)

        if step_url == self.COMPANY:
            company_number = self.request.GET.get('company_number')
            if not company_number:
                return SimpleTemplateResponse(
                    'company-form-error.html',
                    {'validation_error': 'Company number not provided.'},
                )

            try:
                self.store_companies_house_profile_in_session_and_validate(
                    session=self.request.session,
                    company_number=company_number
                )
            except ValidationError as error:
                return SimpleTemplateResponse(
                    'company-form-error.html',
                    {'validation_error': error.message},
                )

        return super().get(*args, **kwargs)

    def get_form_initial(self, step):
        if step == self.COMPANY:
            return forms.get_company_form_initial_data(
                data=helpers.get_company_from_session(self.request.session)
            )

    def serialize_form_data(self):
        data = forms.serialize_enrolment_forms(self.get_all_cleaned_data())
        date_of_creation = helpers.get_company_date_of_creation_from_session(
            self.request.session
        )
        company_name = helpers.get_company_name_from_session(
            self.request.session
        )
        company_number = helpers.get_company_number_from_session(
            self.request.session
        )
        data['sso_id'] = self.request.sso_user.id
        data['company_email'] = self.request.sso_user.email
        data['company_number'] = company_number
        data['date_of_creation'] = date_of_creation
        data['company_name'] = company_name
        return data

    def done(self, *args, **kwargs):
        data = self.serialize_form_data()
        response = api_client.registration.send_form(data)
        if response.ok:
            template = self.success_template
        else:
            template = self.failure_template
        return TemplateResponse(self.request, template)

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(
            form_labels=self.form_labels, *args, **kwargs
        )
        return ctx


class CompaniesHouseSearchApiView(View):
    form_class = forms.CompaniesHouseSearchForm

    def dispatch(self, *args, **kwargs):
        if not settings.NEW_LANDING_PAGE_FEATURE_ENABLED:
            raise Http404()
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(data=request.GET)
        if not form.is_valid():
            return JsonResponse(form.errors, status=400)
        api_response = helpers.CompaniesHouseClient.search(
            term=form.cleaned_data['term']
        )
        api_response.raise_for_status()
        return JsonResponse(api_response.json()['items'], safe=False)
