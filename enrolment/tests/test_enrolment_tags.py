from directory_validators.constants import choices

from enrolment import forms
from enrolment.templatetags import enrolment_tags


def test_no_export_intention_invalid_form():
    form = forms.CompanyExportStatusForm(data={
        'export_status': ''
    })
    assert enrolment_tags.no_export_intention(form) is False


def test_no_export_intention_invalid_form_no_intention():
    form = forms.CompanyExportStatusForm(data={
        'export_status': choices.NO_EXPORT_INTENTION
    })
    assert enrolment_tags.no_export_intention(form) is True


def test_no_export_intention_valid_form():
    form = forms.CompanyExportStatusForm(data={
        'export_status': choices.EXPORT_STATUSES[1][0]
    })
    assert enrolment_tags.no_export_intention(form) is False
