import os

from formtools.wizard.views import SessionWizardView

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views.generic import TemplateView

from company import forms, helpers

from api_client import api_client
from enrolment.views import UserCompanyBaseView


class SupplierCaseStudyView(UserCompanyBaseView, SessionWizardView):

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


class UserCompanyProfileDetailView(UserCompanyBaseView, TemplateView):
    template_name = 'company-profile-details.html'

    def get_context_data(self, **kwargs):
        response = api_client.company.retrieve_profile(
            sso_user_id=self.request.sso_user.id
        )
        if not response.ok:
            response.raise_for_status()
        return {
            'company': helpers.inflate_company_profile_from_response(response)
        }
