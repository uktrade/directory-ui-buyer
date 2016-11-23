from django import forms

# from directory_validators import enrolment as shared_enrolment_validators
from directory_validators.constants import choices


PLEASE_SELECT = 'Please select an option'


class CaseStudyBasicInfoForm(forms.Form):
    title = forms.CharField(
        max_length=100,
    )
    description = forms.CharField(
        max_length=1000,
    )
    sector = forms.ChoiceField(
        choices=['', PLEASE_SELECT] + list(choices.COMPANY_CLASSIFICATIONS),
    )
    website = forms.URLField(
        required=False
    )
    year = forms.CharField()
    tags = forms.CharField(
        max_length=100,
    )


class CaseStudyRichMediaForm(forms.Form):
    image_one = forms.FileField(
        required=False,
        # validators=[shared_enrolment_validators.case_study_image_filesize]
    )
    image_two = forms.FileField(
        required=False,
        # validators=[shared_enrolment_validators.case_study_image_filesize]
    )
    image_three = forms.FileField(
        required=False,
        # validators=[shared_enrolment_validators.case_study_image_filesize]
    )
    video = forms.FileField(
        required=False,
        # validators=[shared_enrolment_validators.case_study_video_filesize]
    )
    testimonial = forms.CharField(
        max_length=1000,
        required=False,
    )


def serialize_supplier_case_study_forms(cleaned_data):
    """
    Return the shape directory-api-client expects for creating and updating
    supplier case studies.

    @param {dict} cleaned_data - All the fields in `CaseStudyRichMediaForm` and
                                `CaseStudyBasicInfoForm`
    @returns dict

    """

    return {
        'title': cleaned_data['title'],
        'description': cleaned_data['description'],
        'sector': cleaned_data['sector'],
        'website': cleaned_data['website'],
        'year': cleaned_data['year'],
        'tags': cleaned_data['tags'],
        'image_one': cleaned_data['image_one'],
        'image_two': cleaned_data['image_two'],
        'image_three': cleaned_data['image_three'],
        'video': cleaned_data['video'],
        'testimonial': cleaned_data['testimonial'],
    }
