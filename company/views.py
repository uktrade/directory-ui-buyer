import http
import os

from formtools.wizard.views import SessionWizardView
import requests

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from company import forms, helpers

from api_client import api_client
from enrolment.helpers import has_verified_company
from sso.utils import SSOLoginRequiredMixin


class SupplierCompanyBaseView(SSOLoginRequiredMixin):

    def dispatch(self, request, *args, **kwargs):
        if request.sso_user is None:
            return self.handle_no_permission()
        else:
            if not has_verified_company(self.request.sso_user.id):
                return redirect('register-instructions')
            else:
                return super(SupplierCompanyBaseView, self).dispatch(
                    request, *args, **kwargs
                )


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

    def done(self, *args, **kwargs):
        api_response = api_client.company.update_profile(
            sso_user_id=self.request.sso_user.id,
            data=self.serialize_form_data()
        )
        if api_response.ok:
            response = redirect('company-detail')
        else:
            response = TemplateResponse(self.request, self.failure_template)
        return response


class SupplierCaseStudyWizardView(SupplierCompanyBaseView, SessionWizardView):

    BASIC = 'basic'
    RICH_MEDIA = 'rich-media'

    failure_template = 'supplier-case-study-error.html'

    file_storage = FileSystemStorage(
        location=os.path.join(settings.MEDIA_ROOT, 'tmp-supplier-media')
    )

    form_list = (
        (BASIC, forms.CaseStudyBasicInfoForm),
        (RICH_MEDIA, forms.CaseStudyRichMediaForm),
    )
    templates = {
        BASIC: 'supplier-case-study-basic-form.html',
        RICH_MEDIA: 'supplier-case-study-rich-media-form.html',
    }
    form_serializer = staticmethod(forms.serialize_supplier_case_study_forms)

    def get_template_names(self):
        return [self.templates[self.steps.current]]

    def get_form_initial(self, step):
        response = api_client.company.retrieve_supplier_case_study(
            sso_user_id=self.request.sso_user.id,
            case_study_id=self.kwargs['id'],
        )
        if not response.ok:
            response.raise_for_status()
        return response.json()

    def serialize_form_data(self):
        return self.form_serializer(self.get_all_cleaned_data())

    def done(self, *args, **kwags):
        data = self.serialize_form_data()
        if self.kwargs['id']:
            response = api_client.company.update_supplier_case_study(
                data=data,
                case_study_id=self.kwargs['id'],
                sso_user_id=self.request.sso_user.id,
            )
        else:
            response = api_client.company.create_supplier_case_study(
                sso_user_id=self.request.sso_user.id,
                data=data,
            )
        if response.ok:
            return redirect('company-detail')
        else:
            return TemplateResponse(self.request, self.failure_template)


class SupplierCompanyProfileDetailView(SupplierCompanyBaseView, TemplateView):
    template_name = 'company-profile-detail.html'

    def get_context_data(self, **kwargs):
        response = api_client.company.retrieve_profile(
            sso_user_id=self.request.sso_user.id
        )
        if not response.ok:
            response.raise_for_status()
        return {
            'company': helpers.get_company_profile_from_response(response),
            'show_edit_links': True,
        }


class PublicProfileListView(SubmitFormOnGetMixin, FormView):
    template_name = 'company-public-profile-list.html'
    form_class = forms.PublicProfileSearchForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context['form']
        if form.is_valid():
            sector = helpers.get_sectors_label(form.cleaned_data['sectors'])
            context['selected_sector_label'] = sector
        return context

    def get_results_and_count(self, form):
        response = api_client.company.list_public_profiles(
            sectors=form.cleaned_data['sectors'],
            page=form.cleaned_data['page']
        )
        if not response.ok:
            response.raise_for_status()
        formatted = helpers.get_company_list_from_response(response)
        return formatted['results'], formatted['count']

    def handle_empty_page(self, form):
        url = '{url}?sectors={sector}'.format(
            url=reverse('public-company-profiles-list'),
            sector=form.cleaned_data['sectors']
        )
        return redirect(url)

    def form_valid(self, form):
        try:
            results, count = self.get_results_and_count(form)
        except requests.exceptions.HTTPError as error:
            if error.response.status_code == http.client.NOT_FOUND:
                # supplier entered a page number returning no results, so
                # redirect them back to the first page
                return self.handle_empty_page(form)
            raise
        else:
            context = self.get_context_data()
            paginator = Paginator(range(count), 10)
            context['pagination'] = paginator.page(form.cleaned_data['page'])
            context['companies'] = results
            return TemplateResponse(self.request, self.template_name, context)


class PublicProfileDetailView(TemplateView):
    template_name = 'company-profile-detail.html'

    def get_context_data(self, **kwargs):
        api_call = (
            api_client.company.
            retrieve_public_profile_by_companies_house_number
        )
        response = api_call(number=self.kwargs['company_number'])
        if not response.ok:
            response.raise_for_status()
        company = helpers.get_public_company_profile_from_response(response)
        return {
            'company': company,
            'show_edit_links': False,
        }


class SupplierCaseStudyDetailView(TemplateView):
    template_name = 'supplier-case-study-detail.html'

    def get_case_study(self):
        response = api_client.company.retrieve_supplier_case_study(
            sso_user_id=self.request.sso_user.id,
            case_study_id=self.kwargs['id'],
        )
        if not response.ok:
            response.raise_for_status()
        return helpers.get_case_study_details_from_response(response)

    def get_context_data(self, **kwargs):
        return {
            'case_study': self.get_case_study(),
        }


class SupplierCompanyProfileEditView(
        SupplierCompanyBaseView,
        UpdateCompanyProfileOnFormWizardDoneMixin,
        SessionWizardView):

    form_list = (
        ('basic', forms.CompanyBasicInfoForm),
        ('classification', forms.CompanyClassificationForm),
    )
    failure_template = 'company-profile-update-error.html'
    templates = {
        'basic': 'company-profile-form.html',
        'classification': 'company-profile-form-classification.html',
    }
    form_serializer = staticmethod(forms.serialize_company_profile_forms)

    def get_form_initial(self, step):
        sso_user_id = self.request.sso_user.id
        response = api_client.company.retrieve_profile(sso_user_id)
        if not response.ok:
            response.raise_for_status()
        return response.json()

    def get_template_names(self):
        return [self.templates[self.steps.current]]


class SupplierCompanyProfileLogoEditView(
        SupplierCompanyBaseView,
        UpdateCompanyProfileOnFormWizardDoneMixin,
        SessionWizardView):

    form_list = (
        ('logo', forms.CompanyLogoForm),
    )
    file_storage = FileSystemStorage(
        location=os.path.join(settings.MEDIA_ROOT, 'tmp-logos')
    )
    failure_template = 'company-profile-update-error.html'
    templates = {
        'logo': 'company-profile-logo-form.html',
    }
    form_serializer = staticmethod(forms.serialize_company_logo_forms)

    def get_template_names(self):
        return [self.templates[self.steps.current]]


class SupplierCompanyDescriptionEditView(
        SupplierCompanyBaseView,
        UpdateCompanyProfileOnFormWizardDoneMixin,
        SessionWizardView):

    form_list = (
        ('description', forms.CompanyDescriptionForm),
    )
    failure_template = 'company-profile-update-error.html'
    templates = {
        'description': 'company-profile-description-form.html',
    }
    form_serializer = staticmethod(forms.serialize_company_description_forms)

    def get_template_names(self):
        return [self.templates[self.steps.current]]

    def get_form_initial(self, step):
        sso_user_id = self.request.sso_user.id
        response = api_client.company.retrieve_profile(sso_user_id)
        if not response.ok:
            response.raise_for_status()
        return response.json()
