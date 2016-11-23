import os

from formtools.wizard.views import SessionWizardView

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from company import forms

from api_client import api_client
from enrolment.views import UserCompanyBaseView


class SupplierCaseStudyView(SessionWizardView):

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
        if self.kwargs['id']:
            response = api_client.company.create(
                data=self.serialize_form_data()
            )
        else:
            response = api_client.company.update(
                data=self.serialize_form_data(),
                id=self.kwargs['id']
            )
        if response.ok:
            return redirect('company-details')
        else:
            return TemplateResponse(self.request, self.failure_template)
