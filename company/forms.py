from django import forms

from directory_validators import company as shared_validators
from directory_validators.constants import choices

from enrolment.forms import IndentedInvalidFieldsMixin, AutoFocusFieldMixin


class CaseStudyBasicInfoForm(IndentedInvalidFieldsMixin, AutoFocusFieldMixin,
                             forms.Form):
    title = forms.CharField(
        max_length=100,
    )
    description = forms.CharField(
        max_length=1000,
        widget=forms.Textarea,
    )
    sector = forms.ChoiceField(
        choices=choices.COMPANY_CLASSIFICATIONS,
    )
    website = forms.URLField(
        max_length=255,
        required=False
    )
    year = forms.CharField(max_length=4)
    keywords = forms.CharField(
        label=(
            'Enter up to 10 keywords that describe your case study '
            '(separated by commas):'
        ),
        help_text=(
            'These keywords will be used to help potential overseas buyers '
            'find your case study.'
        ),
        max_length=1000,
        widget=forms.Textarea,
        validators=[shared_validators.keywords_word_limit]
    )


class CaseStudyRichMediaForm(IndentedInvalidFieldsMixin, AutoFocusFieldMixin,
                             forms.Form):
    image_one = forms.FileField(
        required=False,
        validators=[shared_validators.case_study_image_filesize]
    )
    image_two = forms.FileField(
        required=False,
        validators=[shared_validators.case_study_image_filesize]
    )
    image_three = forms.FileField(
        required=False,
        validators=[shared_validators.case_study_image_filesize]
    )
    testimonial = forms.CharField(
        max_length=1000,
        required=False,
        widget=forms.Textarea,
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
        'keywords': cleaned_data['keywords'],
        'image_one': cleaned_data['image_one'],
        'image_two': cleaned_data['image_two'],
        'image_three': cleaned_data['image_three'],
        'testimonial': cleaned_data['testimonial'],
    }
