import itertools
from unittest.mock import Mock, patch

from directory_constants.constants import choices
import pytest

from django.forms.fields import Field
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.validators import URLValidator

from company import forms, validators
from company.forms import shared_enrolment_validators, shared_validators
from company.tests import helpers
from enrolment.forms import AutoFocusFieldMixin, IndentedInvalidFieldsMixin


URL_FORMAT_MESSAGE = URLValidator.message
REQUIRED_MESSAGE = Field.default_error_messages['required']


@pytest.fixture()
def uploaded_png_image():
    png_image = helpers.create_test_image('png')
    return SimpleUploadedFile(
        name='image.png',
        content=png_image.read(),
        content_type='image/png',
    )


def test_serialize_case_study_forms_string_images():
    data = {
        'title': 'a title',
        'description': 'a description',
        'short_summary': 'damn good',
        'sector': choices.INDUSTRIES[1][0],
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
        'sector': choices.INDUSTRIES[1][0],
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

    actual = forms.serialize_case_study_forms(data)

    assert actual == expected


def test_serialize_case_study_forms_file_images():
    image_one = SimpleUploadedFile(name='image_one', content=b'one')
    image_two = SimpleUploadedFile(name='image_two', content=b'one')
    image_three = SimpleUploadedFile(name='image_three', content=b'one')
    data = {
        'title': 'a title',
        'description': 'a description',
        'short_summary': 'damn good',
        'sector': choices.INDUSTRIES[1][0],
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
        'sector': choices.INDUSTRIES[1][0],
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

    actual = forms.serialize_case_study_forms(data)

    assert actual == expected


def test_case_study_basic_info_validators():
    fields = forms.CaseStudyBasicInfoForm().fields
    for field in [fields['short_summary'], fields['description']]:
        assert validators.does_not_contain_email in field.validators
    assert (
        shared_validators.keywords_word_limit in fields['keywords'].validators
    )


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
        'sector': choices.INDUSTRIES[1][0],
        'website': 'http://www.example.com',
        'keywords': 'goog, great',
    }
    form = forms.CaseStudyBasicInfoForm(data=data)

    assert form.is_valid() is True
    assert form.cleaned_data == data


def test_case_study_rich_media_image_one_update_help_text():
    form = forms.CaseStudyRichMediaForm(initial={'image_one': '123'})
    expected_values = forms.CaseStudyRichMediaForm.help_text_maps[0]

    assert form['image_one'].label == expected_values['update_label']
    assert form['image_one'].help_text == (
        expected_values['update_help_text'].format(initial_value='123')
    )


def test_case_study_rich_media_image_one_create_help_text():
    form = forms.CaseStudyRichMediaForm(initial={'image_one': None})
    expected_values = forms.CaseStudyRichMediaForm.help_text_maps[0]

    assert form['image_one'].label == expected_values['create_label']
    assert form['image_one'].help_text == expected_values['create_help_text']


def test_case_study_rich_media_image_two_update_help_text():
    form = forms.CaseStudyRichMediaForm(initial={'image_two': '123'})
    expected_values = forms.CaseStudyRichMediaForm.help_text_maps[1]

    assert form['image_two'].label == expected_values['update_label']
    assert form['image_two'].help_text == (
        expected_values['update_help_text'].format(initial_value='123')
    )


def test_case_study_rich_media_image_two_create_help_text():
    form = forms.CaseStudyRichMediaForm(initial={'image_two': None})
    expected_values = forms.CaseStudyRichMediaForm.help_text_maps[1]

    assert form['image_two'].label == expected_values['create_label']
    assert form['image_two'].help_text == expected_values['create_help_text']


def test_case_study_rich_media_image_three_update_help_text():
    form = forms.CaseStudyRichMediaForm(initial={'image_three': '123'})
    expected_values = forms.CaseStudyRichMediaForm.help_text_maps[2]

    assert form['image_three'].label == expected_values['update_label']
    assert form['image_three'].help_text == (
        expected_values['update_help_text'].format(initial_value='123')
    )


def test_case_study_rich_media_image_three_create_help_text():
    form = forms.CaseStudyRichMediaForm(initial={'image_three': None})
    expected_values = forms.CaseStudyRichMediaForm.help_text_maps[2]

    assert form['image_three'].label == expected_values['create_label']
    assert form['image_three'].help_text == expected_values['create_help_text']


def test_case_study_rich_media_validators():
    form = forms.CaseStudyRichMediaForm()

    for field_name in ['image_one', 'image_two', 'image_three']:
        field_validators = form.fields[field_name].validators
        assert shared_validators.case_study_image_filesize in field_validators
        assert shared_validators.image_format in field_validators


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
        'sectors': choices.INDUSTRIES[1][0]
    }
    form = forms.PublicProfileSearchForm(data=data)

    assert form.is_valid() is True
    assert form.cleaned_data['page'] == 1


def test_public_profile_search_form_specified_page():
    data = {
        'sectors': choices.INDUSTRIES[1][0],
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
        'sectors': choices.INDUSTRIES[1][0],
    }
    form = forms.PublicProfileSearchForm(data=data)

    assert form.is_valid() is True


def test_company_logo_form_accepts_valid_data(uploaded_png_image):
    form = forms.CompanyLogoForm(files={'logo': uploaded_png_image})

    valid = form.is_valid()

    assert valid is True
    assert form.cleaned_data == {
        'logo': uploaded_png_image,
    }


def test_company_logo_form_logo_is_required():
    form = forms.CompanyLogoForm(files={'logo': None})

    valid = form.is_valid()

    assert valid is False
    assert 'logo' in form.errors
    assert 'This field is required.' in form.errors['logo']


def test_company_profile_logo_validator():
    form = forms.CompanyLogoForm()
    field_validators = form.fields['logo'].validators

    assert shared_enrolment_validators.logo_filesize in field_validators
    assert shared_validators.image_format in field_validators


def test_company_description_form_field_lengths():
    form = forms.CompanyDescriptionForm()

    assert form.fields['description'].max_length == 2000
    assert form.fields['summary'].max_length == 250


def test_company_description_form_field_validators():
    fields = forms.CompanyDescriptionForm().fields
    for field in [fields['summary'], fields['description']]:
        assert validators.does_not_contain_email in field.validators


def test_company_description_form_accepts_valid_data():
    form = forms.CompanyDescriptionForm(data={
        'description': 'thing',
        'summary': 'good',
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
    assert form.errors['keywords'] == [REQUIRED_MESSAGE]
    assert form.errors['employees'] == [REQUIRED_MESSAGE]
    assert 'website' not in form.errors


def test_company_profile_form_keywords_validator():
    field = forms.CompanyBasicInfoForm.base_fields['keywords']
    assert shared_validators.keywords_word_limit in field.validators
    assert shared_validators.keywords_special_characters in field.validators


def test_company_profile_form_url_validator():
    field = forms.CompanyBasicInfoForm.base_fields['website']
    assert isinstance(field.validators[0], URLValidator)


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
        'employees': '1-10',
        'keywords': 'Jolly good exporter',
        'name': 'Example ltd.',
        'postal_full_name': 'Jeremy postal',
        'sectors': '1',
        'website': 'http://example.com',
        'export_destinations': ['CN'],
        'export_destinations_other': 'Portland',
        'has_exported_before': True,
    })
    expected = {
        'keywords': 'Jolly good exporter',
        'employees': '1-10',
        'name': 'Example ltd.',
        'sectors': ['1'],
        'website': 'http://example.com',
        'postal_full_name': 'Jeremy postal',
        'export_destinations': ['CN'],
        'export_destinations_other': 'Portland',
        'has_exported_before': True,
    }
    assert actual == expected


def test_serialize_company_profile_without_address_forms():
    actual = forms.serialize_company_profile_without_address_forms({
        'employees': '1-10',
        'keywords': 'Jolly good exporter',
        'name': 'Example ltd.',
        'sectors': '1',
        'website': 'http://example.com',
        'export_destinations': ['CN'],
        'export_destinations_other': 'Portland',
        'has_exported_before': True,
    })
    expected = {
        'employees': '1-10',
        'keywords': 'Jolly good exporter',
        'name': 'Example ltd.',
        'sectors': ['1'],
        'website': 'http://example.com',
        'export_destinations': ['CN'],
        'export_destinations_other': 'Portland',
        'has_exported_before': True,
    }
    assert actual == expected


def test_serialize_company_logo_form(uploaded_png_image):
    actual = forms.serialize_company_logo_form({'logo': uploaded_png_image})
    expected = {'logo': uploaded_png_image}

    assert actual == expected


def test_serialize_company_description_form():
    actual = forms.serialize_company_description_form({
        'description': 'Jolly good exporter.',
        'summary': 'Nice and good'
    })
    expected = {
        'description': 'Jolly good exporter.',
        'summary': 'Nice and good',
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
        'sectors': 'one',
        'export_destinations': ['CN'],
        'export_destinations_other': 'Portland',
    }
    expected = {
        'sectors': ['one'],
        'export_destinations': ['CN'],
        'export_destinations_other': 'Portland',
    }
    assert forms.serialize_company_sectors_form(data) == expected


def test_serialize_company_contact_form():
    data = {
        'email_full_name': 'Jim',
        'email_address': 'jim@example.com',
        'website': 'http://www.example.com',
    }
    expected = {
        'email_full_name': 'Jim',
        'email_address': 'jim@example.com',
        'website': 'http://www.example.com',
    }
    assert forms.serialize_company_contact_form(data) == expected


def test_serialize_company_address_form():

    actual = forms.serialize_company_address_form({
        'postal_full_name': 'Jeremy postal',
    })
    expected = {
        'postal_full_name': 'Jeremy postal',
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
        'website': 'http://www.example.com',
    }
    form = forms.CompanyContactDetailsForm(data=data)

    assert form.is_valid() is True
    assert form.cleaned_data == data


def test_company_address_verification_required_fields():
    form = forms.CompanyAddressVerificationForm(data={})

    assert form.fields['postal_full_name'].required is True
    assert form.fields['address_confirmed'].required is True


def test_company_address_verification_accepts_valid():
    data = {
        'postal_full_name': 'Jim Example',
        'address_confirmed': True,
    }
    form = forms.CompanyAddressVerificationForm(data=data)

    assert form.is_valid() is True
    assert form.cleaned_data == data


def test_is_optional_profile_values_set_all_set(retrieve_profile_data):
    assert forms.is_optional_profile_values_set(retrieve_profile_data) is True


def test_is_optional_profile_values_set_some_missing(retrieve_profile_data):
    optional_fields = [
        'sectors',
        'keywords',
        'employees',
        'postal_full_name',
    ]

    for field in optional_fields:
        data = retrieve_profile_data.copy()
        del data[field]
        assert forms.is_optional_profile_values_set(data) is False


def test_is_optional_profile_values_set_some_empty(retrieve_profile_data):
    retrieve_profile_data['verified_with_preverified_enrolment'] = False
    field_names = [
        'sectors',
        'keywords',
        'employees',
        'postal_full_name',
    ]
    empty_values = ['', 0, {}, False, []]

    for field_name, value in itertools.product(field_names, empty_values):
        data = retrieve_profile_data.copy()
        data[field_name] = value
        assert forms.is_optional_profile_values_set(data) is False


def test_is_optional_profile_values_preverified_address_missing(
    retrieve_profile_data
):
    retrieve_profile_data['verified_with_preverified_enrolment'] = True
    field_names = [
        'postal_full_name',
    ]
    empty_values = ['', 0, {}, False, []]

    for field_name, value in itertools.product(field_names, empty_values):
        data = retrieve_profile_data.copy()
        data[field_name] = value
        assert forms.is_optional_profile_values_set(data) is True


def test_is_optional_profile_values_preverified_address_present(
    retrieve_profile_data
):
    retrieve_profile_data['verified_with_preverified_enrolment'] = True
    retrieve_profile_data['postal_full_name'] = 'Jim Example'

    assert forms.is_optional_profile_values_set(retrieve_profile_data) is True


def test_is_optional_profile_values_set_none_set():
    data = {'verified_with_preverified_enrolment': False}
    assert forms.is_optional_profile_values_set(data) is False


@patch('company.validators.api_client.company.verify_with_code')
def test_company_address_verification_valid_code(mock_verify_with_code):
    mock_verify_with_code.return_value = Mock(ok=False)

    form = forms.CompanyCodeVerificationForm(
        sso_session_id=1,
        data={'code': 'x'*12}
    )

    assert form.is_valid() is False
    assert form.errors['code'] == [validators.MESSAGE_INVALID_CODE]


@patch('company.validators.api_client.company.verify_with_code')
def test_company_address_verification_invalid_code(mock_verify_with_code):
    mock_verify_with_code.return_value = Mock(ok=True)

    form = forms.CompanyCodeVerificationForm(
        sso_session_id=1,
        data={'code': 'x'*12}
    )

    assert form.is_valid() is True


@patch('company.validators.api_client.company.verify_with_code')
def test_company_address_verification_too_long(mock_verify_with_code):
    mock_verify_with_code.return_value = Mock(ok=True)

    form = forms.CompanyCodeVerificationForm(
        sso_session_id=1,
        data={'code': 'x'*13}
    )
    expected = 'Ensure this value has at most 12 characters (it has 13).'

    assert form.is_valid() is False
    assert form.errors['code'] == [expected]


@patch('company.validators.api_client.company.verify_with_code')
def test_company_address_verification_too_short(mock_verify_with_code):
    mock_verify_with_code.return_value = Mock(ok=True)

    form = forms.CompanyCodeVerificationForm(
        sso_session_id=1,
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


@pytest.mark.parametrize('field', [
    forms.CaseStudyBasicInfoForm().fields['title'],
    forms.CaseStudyBasicInfoForm().fields['short_summary'],
    forms.CaseStudyBasicInfoForm().fields['description'],
    forms.CaseStudyBasicInfoForm().fields['keywords'],
    forms.CaseStudyRichMediaForm().fields['image_one_caption'],
    forms.CaseStudyRichMediaForm().fields['image_two_caption'],
    forms.CaseStudyRichMediaForm().fields['image_three_caption'],
    forms.CaseStudyRichMediaForm().fields['testimonial'],
    forms.CaseStudyRichMediaForm().fields['testimonial_name'],
    forms.CaseStudyRichMediaForm().fields['testimonial_job_title'],
    forms.CaseStudyRichMediaForm().fields['testimonial_company'],
    forms.CompanyBasicInfoForm().fields['name'],
    forms.CompanyBasicInfoForm().fields['keywords'],
    forms.CompanyDescriptionForm().fields['summary'],
    forms.CompanyDescriptionForm().fields['description'],
    forms.CompanyClassificationForm().fields['export_destinations_other'],
    forms.CompanyContactDetailsForm().fields['email_full_name'],
    forms.CompanyAddressVerificationForm().fields['postal_full_name'],
])
def test_xss_attack(field):
    assert shared_validators.no_html in field.validators


@pytest.mark.parametrize('form_class', [
    forms.AddCollaboratorForm,
    forms.TransferAccountEmailForm,
])
def test_add_collaborator_prevents_sending_to_self(form_class):
    form = form_class(
        sso_email_address='dev@example.com',
        data={'email_address': 'dev@example.com'}
    )

    assert form.is_valid() is False
    assert form.errors['email_address'] == [form.MESSAGE_CANNOT_SEND_TO_SELF]


@pytest.mark.parametrize('form_class', [
    forms.AddCollaboratorForm,
    forms.TransferAccountEmailForm,
])
def test_add_collaborator_allows_sending_to_other(form_class):
    form = form_class(
        sso_email_address='dev@example.com',
        data={'email_address': 'dev+1@example.com'}
    )

    assert form.is_valid() is True
