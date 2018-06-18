import pytest
from django.urls import resolve


@pytest.mark.parametrize(
    'path,view_name',
    [
        ('/confirm-company-address/', 'verify-company-address-historic-url'),
        ('/register/foo/', 'register'),
        ('/register-submit/', 'register-submit'),
        ('/company-profile/', 'company-detail'),
        ('/company-profile/edit/', 'company-edit'),
        ('/company-profile/edit/logo/', 'company-edit-logo'),
        ('/company-profile/edit/description/', 'company-edit-description'),
        ('/company-profile/edit/key-facts/', 'company-edit-key-facts'),
        ('/company-profile/edit/sectors/', 'company-edit-sectors'),
        ('/company-profile/edit/contact/', 'company-edit-contact'),
        ('/company-profile/edit/address/', 'company-edit-address'),
        ('/company-profile/edit/social-media/', 'company-edit-social-media'),
        ('/company/case-study/edit/2/', 'company-case-study-edit'),
        ('/company/case-study/create/', 'company-case-study-create'),
        ('/unsubscribe/', 'unsubscribe'),
        ('/verify/', 'verify-company-hub'),
        ('/verify/letter-send/', 'verify-company-address'),
        ('/verify/letter-confirm/', 'verify-company-address-confirm'),
        ('/verify/companies-house/', 'verify-companies-house'),
        (
            '/companies-house-oauth2-callback/',
            'verify-companies-house-callback'
        ),
        ('/account/add-collaborator/', 'add-collaborator'),
        ('/account/remove-collaborator/', 'remove-collaborator'),
        ('/account/transfer/', 'account-transfer'),
        ('/account/transfer/accept/', 'account-transfer-accept'),
        ('/account/collaborate/accept/', 'account-collaborate-accept')
    ]
)
def test_urls_resolve(path, view_name):
    assert resolve(path).view_name == view_name
