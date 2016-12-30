import itertools
from unittest.mock import Mock, patch

from directory_validators.constants import choices
import pytest

from django.forms.fields import Field
from django.forms import CharField, Form
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.validators import URLValidator

from company import forms, validators
from company.forms import shared_enrolment_validators, shared_validators
from enrolment.forms import AutoFocusFieldMixin, IndentedInvalidFieldsMixin


URL_FORMAT_MESSAGE = URLValidator.message
REQUIRED_MESSAGE = Field.default_error_messages['required']


@pytest.fixture
def company_profile():
    return {
        'name': 'Example corp',
        'website': 'http://www.example.com',
        'sectors': [choices.COMPANY_CLASSIFICATIONS[1][0]],
        'keywords': 'Thing, Thinger',
        'employees': choices.EMPLOYEES[1][0],
        'contact_details': {
            'full_name': 'Jim Example'
        },
    }


def create_mock_file():
    return Mock(size=1)


def test_serialize_supplier_case_study_forms_string_images():
    data = {
        'title': 'a title',
        'description': 'a description',
        'short_summary': 'damn good',
        'sector': choices.COMPANY_CLASSIFICATIONS[1][0],
        'website': 'http://www.example.com',
        'keywords': 'goog, great',
        'image_one': '1.png',
        'image_two': '2.png',
        'image_three': '3.png',
        'image_one_caption': 'image one caption',
        'image_two_caption': 'image two caption',
        'image_three_caption': 'image three caption',
        'testimonial': 'very nice',
        'testimonial_name': 'Neville',
        'testimonial_job_title': 'Abstract hat maker',
        'testimonial_company': 'Imaginary hats Ltd',
    }
    expected = {
        'title': 'a title',
        'description': 'a description',
        'short_summary': 'damn good',
        'sector': choices.COMPANY_CLASSIFICATIONS[1][0],
        'website': 'http://www.example.com',
        'keywords': 'goog, great',
        'testimonial': 'very nice',
        'testimonial_name': 'Neville',
        'testimonial_job_title': 'Abstract hat maker',
        'testimonial_company': 'Imaginary hats Ltd',
        'image_one_caption': 'image one caption',
        'image_two_caption': 'image two caption',
        'image_three_caption': 'image three caption',
    }

    actual = forms.serialize_supplier_case_study_forms(data)

    assert actual == expected


def test_serialize_supplier_case_study_forms_file_images():
    image_one = SimpleUploadedFile(name='image_one', content=b'one')
    image_two = SimpleUploadedFile(name='image_two', content=b'one')
    image_three = SimpleUploadedFile(name='image_three', content=b'one')
    data = {
        'title': 'a title',
        'description': 'a description',
        'short_summary': 'damn good',
        'sector': choices.COMPANY_CLASSIFICATIONS[1][0],
        'website': 'http://www.example.com',
        'keywords': 'goog, great',
        'image_one': image_one,
        'image_two': image_two,
        'image_three': image_three,
        'image_one_caption': 'image one caption',
        'image_two_caption': 'image two caption',
        'image_three_caption': 'image three caption',
        'testimonial': 'very nice',
        'testimonial_name': 'Neville',
        'testimonial_job_title': 'Abstract hat maker',
        'testimonial_company': 'Imaginary hats Ltd',
    }
    expected = {
        'title': 'a title',
        'description': 'a description',
        'short_summary': 'damn good',
        'sector': choices.COMPANY_CLASSIFICATIONS[1][0],
        'website': 'http://www.example.com',
        'keywords': 'goog, great',
        'testimonial': 'very nice',
        'testimonial_name': 'Neville',
        'testimonial_job_title': 'Abstract hat maker',
        'testimonial_company': 'Imaginary hats Ltd',
        'image_one': image_one,
        'image_two': image_two,
        'image_three': image_three,
        'image_one_caption': 'image one caption',
        'image_two_caption': 'image two caption',
        'image_three_caption': 'image three caption',
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
    assert form.errors['keywords'] == [REQUIRED_MESSAGE]


def test_case_study_form_sectors_contains_empty_choice():
    form = forms.CaseStudyBasicInfoForm(data={})

    assert form.fields['sector'].choices[0] == ('', 'Select Sector')


def test_case_study_form_all_fields():
    data = {
        'title': 'a title',
        'description': 'a description',
        'short_summary': 'damn good',
        'sector': choices.COMPANY_CLASSIFICATIONS[1][0],
        'website': 'http://www.example.com',
        'keywords': 'goog, great',
    }
    form = forms.CaseStudyBasicInfoForm(data=data)

    assert form.is_valid() is True
    assert form.cleaned_data == data


def test_case_study_rich_media_required():
    form = forms.CaseStudyRichMediaForm()
    assert form.fields['image_one'].required is True
    assert form.fields['image_one_caption'].required is True
    assert form.fields['image_two'].required is False
    assert form.fields['image_two_caption'].required is False
    assert form.fields['image_three'].required is False
    assert form.fields['image_three_caption'].required is False


def test_case_study_rich_media_max_length():
    form = forms.CaseStudyRichMediaForm()

    assert form.fields['image_one_caption'].max_length == 120
    assert form.fields['image_two_caption'].max_length == 120
    assert form.fields['image_three_caption'].max_length == 120


def test_case_study_basic_info_max_length():
    form = forms.CaseStudyBasicInfoForm()

    assert form.fields['short_summary'].max_length == 200
    assert form.fields['title'].max_length == 60
    assert form.fields['description'].max_length == 1000
    assert form.fields['keywords'].max_length == 1000
    assert form.fields['website'].max_length == 255


def test_auto_focus_mixin_installed():
    FormClasses = [
        forms.CaseStudyBasicInfoForm,
        forms.CaseStudyRichMediaForm,
        forms.CompanyAddressVerificationForm,
        forms.CompanyBasicInfoForm,
        forms.CompanyClassificationForm,
        forms.CompanyContactDetailsForm,
        forms.CompanyDescriptionForm,
        forms.CompanyLogoForm,
        forms.PublicProfileSearchForm,
    ]
    for FormClass in FormClasses:
        assert issubclass(FormClass, AutoFocusFieldMixin)


def test_indent_invalid_mixin_installed():
    FormClasses = [
        forms.CaseStudyBasicInfoForm,
        forms.CaseStudyRichMediaForm,
        forms.CompanyAddressVerificationForm,
        forms.CompanyBasicInfoForm,
        forms.CompanyClassificationForm,
        forms.CompanyContactDetailsForm,
        forms.CompanyDescriptionForm,
        forms.CompanyLogoForm,
        forms.PublicProfileSearchForm,
    ]
    for FormClass in FormClasses:
        assert issubclass(FormClass, IndentedInvalidFieldsMixin)


def test_public_profile_search_form_default_page():
    data = {
        'sectors': choices.COMPANY_CLASSIFICATIONS[1][0]
    }
    form = forms.PublicProfileSearchForm(data=data)

    assert form.is_valid() is True
    assert form.cleaned_data['page'] == 1


def test_public_profile_search_form_specified_page():
    data = {
        'sectors': choices.COMPANY_CLASSIFICATIONS[1][0],
        'page': 3
    }
    form = forms.PublicProfileSearchForm(data=data)

    assert form.is_valid() is True
    assert form.cleaned_data['page'] == 3


def test_public_profile_search_form_requires_sectors():
    data = {}
    form = forms.PublicProfileSearchForm(data=data)

    assert form.is_valid() is False
    assert form.errors['sectors'] == [REQUIRED_MESSAGE]


def test_public_profile_search_form_valid_data():
    data = {
        'sectors': choices.COMPANY_CLASSIFICATIONS[1][0],
    }
    form = forms.PublicProfileSearchForm(data=data)

    assert form.is_valid() is True


def test_company_logo_form_accepts_valid_data():
    logo = create_mock_file()
    form = forms.CompanyLogoForm(files={'logo': logo})

    valid = form.is_valid()

    assert valid is True
    assert form.cleaned_data == {
        'logo': logo,
    }


def test_company_logo_form_logo_is_required():
    form = forms.CompanyLogoForm(files={'logo': None})

    valid = form.is_valid()

    assert valid is False
    assert 'logo' in form.errors
    assert 'This field is required.' in form.errors['logo']


def test_company_profile_logo_validator():
    field = forms.CompanyLogoForm.base_fields['logo']
    assert shared_enrolment_validators.logo_filesize in field.validators


def test_company_description_form_accepts_valid_data():
    form = forms.CompanyDescriptionForm(data={
        'description': 'thing'
    })
    assert form.is_valid() is True
    assert form.cleaned_data['description'] == 'thing'


def test_company_description_form_rejects_invalid_data():
    form = forms.CompanyDescriptionForm(data={})
    assert form.is_valid() is False
    assert form.errors['description'] == [REQUIRED_MESSAGE]


def test_company_profile_form_required_fields():
    form = forms.CompanyBasicInfoForm(data={})

    valid = form.is_valid()

    assert valid is False
    assert form.errors['name'] == [REQUIRED_MESSAGE]
    assert form.errors['website'] == [REQUIRED_MESSAGE]
    assert form.errors['keywords'] == [REQUIRED_MESSAGE]


def test_company_profile_form_keywords_validator():
    field = forms.CompanyBasicInfoForm.base_fields['keywords']
    assert shared_validators.keywords_word_limit in field.validators


def test_company_profile_form_url_validator():
    field = forms.CompanyBasicInfoForm.base_fields['website']
    assert isinstance(field.validators[0], URLValidator)


def test_company_classification_form_sectors_validator():
    field = forms.CompanyClassificationForm.base_fields['sectors']
    assert shared_validators.sector_choice_limit in field.validators


def test_company_profile_form_accepts_valid_data():
    data = {
        'name': 'Amazon UK',
        'website': 'http://amazon.co.uk',
        'keywords': 'Ecommerce',
        'employees': '1-10',
    }
    form = forms.CompanyBasicInfoForm(data=data)

    valid = form.is_valid()

    assert valid is True
    assert form.cleaned_data == {
        'name': 'Amazon UK',
        'website': 'http://amazon.co.uk',
        'keywords': 'Ecommerce',
        'employees': '1-10',
    }


def test_serialize_company_profile_forms():

    actual = forms.serialize_company_profile_forms({
        'address_line_1': '123 Fake Street',
        'address_line_2': 'Fakeville',
        'country': 'GB',
        'email_address': 'Jeremy@example.com',
        'email_full_name': 'Jeremy email',
        'employees': '1-10',
        'keywords': 'Jolly good exporter.',
        'locality': 'London',
        'name': 'Example ltd.',
        'po_box': '124',
        'postal_code': 'E14 9IX',
        'postal_full_name': 'Jeremy postal',
        'sectors': ['1', '2'],
        'website': 'http://example.com',
    })
    expected = {
        'keywords': 'Jolly good exporter.',
        'employees': '1-10',
        'name': 'Example ltd.',
        'sectors': ['1', '2'],
        'website': 'http://example.com',
        'contact_details': {
            'address_line_1': '123 Fake Street',
            'address_line_2': 'Fakeville',
            'country': 'GB',
            'email_address': 'Jeremy@example.com',
            'email_full_name': 'Jeremy email',
            'locality': 'London',
            'po_box': '124',
            'postal_code': 'E14 9IX',
            'postal_full_name': 'Jeremy postal',
        }
    }
    assert actual == expected


def test_serialize_company_logo_form():
    logo = create_mock_file()
    actual = forms.serialize_company_logo_form({
        'logo': logo,
    })
    expected = {
        'logo': logo,
    }
    assert actual == expected


def test_serialize_company_description_form():
    actual = forms.serialize_company_description_form({
        'description': 'Jolly good exporter.',
    })
    expected = {
        'description': 'Jolly good exporter.',
    }
    assert actual == expected


def test_serialize_company_basic_info_form():
    data = {
        'name': 'Jim example',
        'website': 'http://www.google.com',
        'keywords': 'good, great',
        'employees': '1-10',
    }
    expected = {
        'name': 'Jim example',
        'website': 'http://www.google.com',
        'keywords': 'good, great',
        'employees': '1-10',
    }
    assert forms.serialize_company_basic_info_form(data) == expected


def test_serialize_company_sectors_form():
    data = {
        'sectors': ['one', 'two']
    }
    expected = {
        'sectors': ['one', 'two']
    }
    assert forms.serialize_company_sectors_form(data) == expected


def test_serialize_company_contact_form():
    data = {
        'email_full_name': 'Jim',
        'email_address': 'jim@example.com',
    }
    expected = {
        'contact_details': {
            'email_full_name': 'Jim',
            'email_address': 'jim@example.com',
        }
    }
    assert forms.serialize_company_contact_form(data) == expected


def test_serialize_company_address_form():

    actual = forms.serialize_company_address_form({
        'address_line_1': '123 Fake Street',
        'address_line_2': 'Fakeville',
        'country': 'GB',
        'keywords': 'Jolly good exporter.',
        'locality': 'London',
        'po_box': '124',
        'postal_code': 'E14 9IX',
        'postal_full_name': 'Jeremy postal',
    })
    expected = {
        'contact_details': {
            'address_line_1': '123 Fake Street',
            'address_line_2': 'Fakeville',
            'country': 'GB',
            'locality': 'London',
            'po_box': '124',
            'postal_code': 'E14 9IX',
            'postal_full_name': 'Jeremy postal',
        }
    }
    assert actual == expected


def test_company_contact_details_rejects_invalid():
    form = forms.CompanyContactDetailsForm(data={})

    assert form.is_valid() is False
    assert form.errors['email_address'] == [REQUIRED_MESSAGE]
    assert form.errors['email_full_name'] == [REQUIRED_MESSAGE]


def test_company_contact_details_accepts_valid():
    data = {
        'email_address': 'Jeremy@exmaple.com',
        'email_full_name': 'Jeremy',
    }
    form = forms.CompanyContactDetailsForm(data=data)

    assert form.is_valid() is True
    assert form.cleaned_data == data


def test_company_address_verification_detects_tamper():
    assert issubclass(
        forms.CompanyAddressVerificationForm, forms.PreventTamperMixin
    )
    assert forms.CompanyAddressVerificationForm.tamper_proof_fields == [
        'address_line_1',
        'address_line_2',
        'locality',
        'country',
        'postal_code',
        'po_box',
    ]


def test_company_address_verification_rejects_invalid():
    form = forms.CompanyAddressVerificationForm(data={})

    assert form.is_valid() is False
    assert form.errors['address_line_1'] == [REQUIRED_MESSAGE]
    assert form.errors['postal_code'] == [REQUIRED_MESSAGE]

    assert 'postal_full_name' not in form.errors
    assert 'address_line_2' not in form.errors
    assert 'locality' not in form.errors
    assert 'po_box' not in form.errors
    assert 'country' not in form.errors


@patch('company.forms.CompanyAddressVerificationForm.is_form_tampered',
       Mock(return_value=False))
def test_company_address_verification_accepts_valid():
    data = {
        'postal_full_name': 'Peter',
        'address_line_1': '123 Fake Street',
        'address_line_2': 'Fakeville',
        'locality': 'London',
        'postal_code': 'E14 8UX',
        'po_box': '123',
        'country': 'GB',
        'signature': '124',
    }
    form = forms.CompanyAddressVerificationForm(data=data)

    assert form.is_valid() is True
    assert form.cleaned_data == data


def test_is_optional_profile_values_set_all_set(company_profile):
    assert forms.is_optional_profile_values_set(company_profile) is True


def test_is_optional_profile_values_set_some_missing(company_profile):
    optional_fields = [
        'name',
        'website',
        'sectors',
        'keywords',
        'employees',
        'contact_details',
    ]

    for field in optional_fields:
        data = company_profile.copy()
        del data[field]
        assert forms.is_optional_profile_values_set(data) is False


def test_is_optional_profile_values_set_some_empty(company_profile):
    field_names = [
        'name',
        'website',
        'sectors',
        'keywords',
        'employees',
        'contact_details',
    ]
    empty_values = [None, '', 0, {}, False, []]

    for field_name, value in itertools.product(field_names, empty_values):
        data = company_profile.copy()
        data[field_name] = value
        assert forms.is_optional_profile_values_set(data) is False


def test_is_optional_profile_values_set_none_set():
    assert forms.is_optional_profile_values_set({}) is False


class PreventTamperForm(forms.PreventTamperMixin, Form):
    tamper_proof_fields = ['field1', 'field2']

    field1 = CharField()
    field2 = CharField()
    field3 = CharField()


class PreventTamperFormBadDataType(forms.PreventTamperMixin, Form):
    tamper_proof_fields = {'field1', 'field2'}

    field1 = CharField()
    field2 = CharField()
    field3 = CharField()


def test_prevent_tamper_rejects_set():
    with pytest.raises(AssertionError):
        PreventTamperFormBadDataType()


def test_prevent_tamper_rejects_change():
    initial = {
        'field1': '123',
        'field2': '456',
    }
    initial_form = PreventTamperForm(initial=initial)
    data = {
        'field1': '123',
        'field2': '456A',
        'field3': 'thing',
        'signature': initial_form.initial['signature']
    }

    form = PreventTamperForm(data=data)
    expected = [forms.PreventTamperMixin.NO_TAMPER_MESSAGE]

    assert form.is_valid() is False
    assert form.errors['__all__'] == expected


def test_prevent_tamper_detects_accepts_unchanged():
    initial = {
        'field1': '123',
        'field2': '456',
    }
    initial_form = PreventTamperForm(initial=initial)
    data = {
        'field1': '123',
        'field2': '456',
        'field3': 'thing',
        'signature': initial_form.initial['signature']
    }

    form = PreventTamperForm(data=data)

    assert form.is_valid() is True


def test_prevent_tamper_detects_accepts_changed_other_field():
    initial = {
        'field1': '123',
        'field2': '456',
        'field3': 'thing1',
    }
    initial_form = PreventTamperForm(initial=initial)
    data = {
        'field1': '123',
        'field2': '456',
        'field3': 'thing2',
        'signature': initial_form.initial['signature']
    }

    form = PreventTamperForm(data=data)

    assert form.is_valid() is True


@patch('company.validators.api_client.company.verify_with_code')
def test_company_address_verification_valid_code(mock_verify_with_code):
    mock_verify_with_code.return_value = Mock(ok=False)

    form = forms.CompanyCodeVerificationForm(
        sso_id=1,
        data={'code': 'x'*12}
    )

    assert form.is_valid() is False
    assert form.errors['code'] == [validators.MESSAGE_INVALID_CODE]


@patch('company.validators.api_client.company.verify_with_code')
def test_company_address_verification_invalid_code(mock_verify_with_code):
    mock_verify_with_code.return_value = Mock(ok=True)

    form = forms.CompanyCodeVerificationForm(
        sso_id=1,
        data={'code': 'x'*12}
    )

    assert form.is_valid() is True


@patch('company.validators.api_client.company.verify_with_code')
def test_company_address_verification_too_long(mock_verify_with_code):
    mock_verify_with_code.return_value = Mock(ok=True)

    form = forms.CompanyCodeVerificationForm(
        sso_id=1,
        data={'code': 'x'*13}
    )
    expected = 'Ensure this value has at most 12 characters (it has 13).'

    assert form.is_valid() is False
    assert form.errors['code'] == [expected]


@patch('company.validators.api_client.company.verify_with_code')
def test_company_address_verification_too_short(mock_verify_with_code):
    mock_verify_with_code.return_value = Mock(ok=True)

    form = forms.CompanyCodeVerificationForm(
        sso_id=1,
        data={'code': 'x'*11}
    )
    expected = 'Ensure this value has at least 12 characters (it has 11).'

    assert form.is_valid() is False
    assert form.errors['code'] == [expected]


def test_social_links_form_all_optional():
    form = forms.SocialLinksForm()

    assert form.fields['twitter_url'].required is False
    assert form.fields['facebook_url'].required is False
    assert form.fields['linkedin_url'].required is False


def test_social_links_validators():
    form = forms.SocialLinksForm()
    twitter_validator = shared_validators.case_study_social_link_twitter
    facebook_validator = shared_validators.case_study_social_link_facebook
    linkedin_validator = shared_validators.case_study_social_link_linkedin

    assert twitter_validator in form.fields['twitter_url'].validators
    assert facebook_validator in form.fields['facebook_url'].validators
    assert linkedin_validator in form.fields['linkedin_url'].validators


def test_serialize_social_links_form():
    actual = forms.serialize_social_links_form({
        'twitter_url': 'twitter_url.com',
        'facebook_url': 'facebook_url.com',
        'linkedin_url': 'linkedin_url.com',
    })

    assert actual == {
        'twitter_url': 'twitter_url.com',
        'facebook_url': 'facebook_url.com',
        'linkedin_url': 'linkedin_url.com',
    }
