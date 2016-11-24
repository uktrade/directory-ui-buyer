from company import forms


def test_serialize_supplier_case_study_forms():
    data = {
        'title': 'a title',
        'description': 'a description',
        'sector': 'a sector',
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
        'sector': 'a sector',
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
