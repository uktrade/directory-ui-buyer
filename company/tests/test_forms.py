from django.forms.fields import Field

from directory_validators import company as shared_validators
from directory_validators.constants import choices

from company import forms

REQUIRED_MESSAGE = Field.default_error_messages['required']


def test_serialize_supplier_case_study_forms():
    data = {
        'title': 'a title',
        'description': 'a description',
        'sector': choices.COMPANY_CLASSIFICATIONS[1][0],
        'website': 'http://www.example.com',
        'year': '2010',
        'keywords': 'goog, great',
        'image_one': '1.png',
        'image_two': '2.png',
        'image_three': '3.png',
        'testimonial': 'very nice',
    }
    expected = {
        'title': 'a title',
        'description': 'a description',
        'sector': choices.COMPANY_CLASSIFICATIONS[1][0],
        'website': 'http://www.example.com',
        'year': '2010',
        'keywords': 'goog, great',
        'image_one': '1.png',
        'image_two': '2.png',
        'image_three': '3.png',
        'testimonial': 'very nice',
    }

    actual = forms.serialize_supplier_case_study_forms(data)

    assert actual == expected


def test_case_study_basic_info_validators():
    field = forms.CaseStudyBasicInfoForm.base_fields['keywords']
    assert shared_validators.keywords_word_limit in field.validators


def test_case_study_form_required_fields():
    form = forms.CaseStudyBasicInfoForm(data={})

    assert form.is_valid() is False
    assert form.errors['title'] == [REQUIRED_MESSAGE]
    assert form.errors['description'] == [REQUIRED_MESSAGE]
    assert form.errors['sector'] == [REQUIRED_MESSAGE]
    assert form.errors['year'] == [REQUIRED_MESSAGE]
    assert form.errors['keywords'] == [REQUIRED_MESSAGE]


def test_case_study_form_all_fields():
    data = {
        'title': 'a title',
        'description': 'a description',
        'sector': choices.COMPANY_CLASSIFICATIONS[1][0],
        'website': 'http://www.example.com',
        'year': '2010',
        'keywords': 'goog, great',
    }
    form = forms.CaseStudyBasicInfoForm(data=data)

    assert form.is_valid() is True
    assert form.cleaned_data == data
