from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views.generic import FormView, View
from django.forms import ValidationError

from formtools.wizard.views import NamedUrlSessionWizardView

from api_client import api_client
from enrolment import forms, helpers
from enrolment.helpers import (
    store_companies_house_profile_in_session_and_validate
)
from sso.utils import SSOLoginRequiredMixin

COMPANY_NUMBER_NOT_PROVIDED_ERROR = 'Company number not provided.'
EXPORT_STATUS_NOT_PROVIDED_ERROR = 'Export status not provided.'


class DomesticLandingView(FormView):
    template_name = 'landing-page.html'
    form_class = forms.CompanyNumberForm
    http_method_names = ['get', 'post']

    def dispatch(self, request, *args, **kwargs):
        if request.sso_user and helpers.has_company(request.sso_user.id):
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


class EnrolmentView(NamedUrlSessionWizardView):

    COMPANY = 'company'
    STATUS = 'exports'

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
        if request.sso_user and helpers.has_company(request.sso_user.id):
            return redirect('company-detail')
        else:
            return super(EnrolmentView, self).dispatch(
                request, *args, **kwargs
            )

    def get_template_names(self):
        return [self.templates[self.steps.current]]

    def get_company_number(self):
        company_number = self.request.GET.get(
            'company_number') or helpers.get_company_number_from_session(
            self.request.session
        )

        if not company_number:
            raise ValidationError(COMPANY_NUMBER_NOT_PROVIDED_ERROR)
        else:
            return company_number

    def get(self, *args, **kwargs):
        if kwargs.get('step') == self.COMPANY:
            try:
                # If the user already performed company lookup and went back
                # to landing page to request a different company
                # we need to reset form wizard storage and update session

                stored_number = helpers.get_company_number_from_session(
                    self.request.session
                )
                requested_number = self.get_company_number()

                if stored_number != requested_number:
                    # Reset form storage to avoid reusing previous company
                    self.storage.reset()

                    # Set new company in session
                    store_companies_house_profile_in_session_and_validate(
                        session=self.request.session,
                        company_number=requested_number
                    )
            except ValidationError as error:
                return helpers.get_error_response(
                    error_message=error.message
                )

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
        export_status = self.get_all_cleaned_data()['export_status']

        url = '{path}?company_number={number}&export_status={status}'.format(
            path=reverse('register-submit'),
            number=company_number,
            status=export_status
        )
        return HttpResponseRedirect(url)

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(
            form_labels=self.form_labels, *args, **kwargs
        )
        return ctx


class SubmitEnrolmentView(SSOLoginRequiredMixin, View):
    success_template = 'registered.html'
    failure_template = 'enrolment-failed.html'

    def dispatch(self, request, *args, **kwargs):
        if request.sso_user is None:
            return self.handle_no_permission()
        elif helpers.has_company(request.sso_user.id):
            return redirect('company-detail')
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_enrolment_data(self, export_status):
        date_of_creation = helpers.get_company_date_of_creation_from_session(
            self.request.session
        )
        company_name = helpers.get_company_name_from_session(
            self.request.session
        )
        company_number = helpers.get_company_number_from_session(
            self.request.session
        )

        return {
            'sso_id': self.request.sso_user.id,
            'company_email': self.request.sso_user.email,
            'contact_email_address': self.request.sso_user.email,
            'company_number': company_number,
            'date_of_creation': date_of_creation,
            'company_name': company_name,
            'export_status': export_status
        }

    def get_company_number(self):
        company_number = self.request.GET.get('company_number')
        if not company_number:
            raise ValidationError(COMPANY_NUMBER_NOT_PROVIDED_ERROR)
        else:
            return company_number

    def get_export_status(self):
        export_status = self.request.GET.get('export_status')
        if not export_status:
            raise ValidationError(EXPORT_STATUS_NOT_PROVIDED_ERROR)
        else:
            return export_status

    def get(self, request, *args, **kwargs):
        try:
            export_status = self.get_export_status()
            helpers.store_companies_house_profile_in_session_and_validate(
                session=self.request.session,
                company_number=self.get_company_number()
            )
        except ValidationError as error:
            return helpers.get_error_response(
                error_message=error.message
            )

        response = api_client.registration.send_form(
            self.get_enrolment_data(export_status=export_status)
        )
        if not response.ok:
            response = TemplateResponse(self.request, self.failure_template)
        elif settings.FEATURE_SYNCHRONOUS_PROFILE_CREATION:
            response = redirect('company-edit')
        else:
            response = TemplateResponse(self.request, self.success_template)
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
