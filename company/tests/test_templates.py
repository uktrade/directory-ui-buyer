from django.urls import reverse
from django.template.loader import render_to_string


def test_company_verify_hub_letter_sent():
    template_name = 'company-verify-hub.html'
    context = {
        'company': {
            'is_verification_letter_sent': True,
        }
    }

    html = render_to_string(template_name, context)

    assert reverse('verify-company-address-confirm') in html
    assert reverse('verify-companies-house') in html


def test_company_verify_hub_letter_not_sent():
    template_name = 'company-verify-hub.html'
    context = {
        'company': {
            'is_verification_letter_sent': False,
        }
    }

    html = render_to_string(template_name, context)

    assert reverse('verify-company-address') in html
    assert reverse('verify-companies-house') in html
