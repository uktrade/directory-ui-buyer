from directory_constants import urls
from directory_api_client.client import api_client
from formtools.wizard.views import SessionWizardView
from requests.exceptions import HTTPError
import sentry_sdk

from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views.generic import RedirectView, TemplateView, View
from django.views.generic.edit import FormView
from django.urls import reverse

from company import forms, helpers
from enrolment.helpers import CompaniesHouseClient


class SubmitFormOnGetMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['data'] = self.request.GET or None
        return kwargs

    def get(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UpdateCompanyProfileOnFormWizardDoneMixin:
    def serialize_form_data(self):
        return self.form_serializer(self.get_all_cleaned_data())

    def handle_profile_update_success(self):
        return redirect('company-detail')

    @staticmethod
    def send_update_error_to_sentry(sso_user, api_response):
        # This is needed to not include POST data (e.g. binary image), which
        # was causing sentry to fail at sending

        sentry_sdk.set_user(
            {'hashed_uuid': sso_user.hashed_uuid, 'user_email': sso_user.email}
        )
        sentry_sdk.set_extra('api_response', str(api_response.content))
        sentry_sdk.capture_message('Updating company profile failed')

    def done(self, *args, **kwargs):
        response = api_client.company.profile_update(
            sso_session_id=self.request.user.session_id,
            data=self.serialize_form_data()
        )
        try:
            response.raise_for_status()
        except HTTPError:
            self.send_update_error_to_sentry(
                sso_user=self.request.user,
                api_response=response
            )
            raise
        else:
            return self.handle_profile_update_success()


class GetTemplateForCurrentStepMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.templates

    def get_template_names(self):
        return [self.templates[self.steps.current]]


class SendVerificationLetterView(
    GetTemplateForCurrentStepMixin,
    UpdateCompanyProfileOnFormWizardDoneMixin,
    SessionWizardView
):

    ADDRESS = 'address'
    SENT = 'sent'

    form_list = (
        (ADDRESS, forms.CompanyAddressVerificationForm),
    )
    templates = {
        ADDRESS: 'company-profile-form-address.html',
        SENT: 'company-profile-form-letter-sent.html',
    }
    form_labels = [
        (ADDRESS, 'Address'),
    ]
    form_serializer = staticmethod(forms.serialize_company_address_form)

    def get_context_data(self, form, **kwargs):
        address = helpers.build_company_address(self.request.user.company)
        context = super().get_context_data(
            form=form,
            form_labels=self.form_labels,
            all_cleaned_data=self.get_all_cleaned_data(),
            company_name=self.request.user.company['name'],
            company_number=self.request.user.company['number'],
            company_address=address,
            **kwargs
        )
        return context

    def handle_profile_update_success(self):
        context = {'profile_url': urls.domestic.SINGLE_SIGN_ON_PROFILE / 'business-profile'}
        return TemplateResponse(self.request, self.templates[self.SENT], context)


class CompanyVerifyView(TemplateView):

    template_name = 'company-verify-hub.html'

    def get_context_data(self, **kwargs):
        return {
            'company': self.request.user.company,
        }


class CompanyAddressVerificationView(
    GetTemplateForCurrentStepMixin,
    SessionWizardView
):

    ADDRESS = 'address'
    SUCCESS = 'success'

    form_list = (
        (ADDRESS, forms.CompanyCodeVerificationForm),
    )
    templates = {
        ADDRESS: 'company-profile-address-verification-form.html',
        SUCCESS: 'company-profile-address-verification-success.html'
    }

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)
        kwargs['sso_session_id'] = self.request.user.session_id
        return kwargs

    def done(self, *args, **kwargs):
        return TemplateResponse(
            self.request,
            self.templates[self.SUCCESS]
        )

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            company=self.request.user.company,
            **kwargs
        )


class CompanyAddressVerificationHistoricView(RedirectView):
    pattern_name = 'verify-company-address'


class EmailUnsubscribeView(FormView):

    form_class = forms.EmptyForm
    template_name = 'email-unsubscribe.html'
    success_template = 'email-unsubscribe-success.html'

    def form_valid(self, form):
        response = api_client.supplier.unsubscribe(
            sso_session_id=self.request.user.session_id
        )
        response.raise_for_status()
        return TemplateResponse(self.request, self.success_template)


class RequestPaylodTooLargeErrorView(TemplateView):
    template_name = 'image-too-large.html'

    def dispatch(self, request, *args, **kwargs):
        # the template has a "click here to go back to the form". We get the
        # url from the referer header.
        if 'HTTP_REFERER' not in request.META:
            return redirect('index')
        return super().dispatch(request, *args, **kwargs)


class Oauth2CallbackUrlMixin:
    @property
    def redirect_uri(self):
        return self.request.build_absolute_uri(
            reverse('verify-companies-house-callback')
        )


class CompaniesHouseOauth2View(Oauth2CallbackUrlMixin, RedirectView):

    def get_redirect_url(self):
        company = helpers.get_company_profile(self.request.user.session_id)
        return CompaniesHouseClient.make_oauth2_url(
            company_number=company['number'],
            redirect_uri=self.redirect_uri,
        )


class CompaniesHouseOauth2CallbackView(
    SubmitFormOnGetMixin,
    Oauth2CallbackUrlMixin,
    FormView
):

    form_class = forms.CompaniesHouseOauth2Form
    template_name = 'companies-house-oauth2-callback.html'
    error_template = 'companies-house-oauth2-error.html'
    success_url = urls.domestic.FIND_A_BUYER

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['redirect_uri'] = self.redirect_uri
        return kwargs

    def form_valid(self, form):
        response = api_client.company.verify_with_companies_house(
            sso_session_id=self.request.user.session_id,
            access_token=form.oauth2_response.json()['access_token']
        )
        if response.status_code == 500:
            return TemplateResponse(self.request, self.error_template)
        else:
            return super().form_valid(form)


class CSVDumpGenericView(View):

    def get(self, request, *args, **kwargs):
        token = request.GET.get('token')
        if not token:
            return HttpResponseForbidden('Token not provided')
        csv_file = self.get_file(token)
        response = HttpResponse(
            csv_file.content, content_type=csv_file.headers['Content-Type']
        )
        response['Content-Disposition'] = csv_file.headers[
            'Content-Disposition'
        ]
        return response


class BuyerCSVDumpView(CSVDumpGenericView):

    @staticmethod
    def get_file(token):
        return api_client.buyer.get_csv_dump(token)


class SupplierCSVDumpView(CSVDumpGenericView):

    @staticmethod
    def get_file(token):
        return api_client.supplier.get_csv_dump(token)
