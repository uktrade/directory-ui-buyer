from unittest.mock import Mock

from django.urls import reverse
from django.views.generic import TemplateView

from company import redirects


class BaseTestView(TemplateView):
    template_name = 'company-profile-detail.html'


class CompanyTestView(BaseTestView):
    @property
    def company_profile(self):
        return {'number': 123456}


class NoCompanyTestView(BaseTestView):
    @property
    def company_profile(self):
        return {}


class VerifiedCompanyTestView(BaseTestView):
    @property
    def company_profile(self):
        return {'is_verified': True}


class UnverifiedCompanyTestView(BaseTestView):
    @property
    def company_profile(self):
        return {'is_verified': False}


class VerificationLetterSentTestView(BaseTestView):
    @property
    def company_profile(self):
        return {'is_verification_letter_sent': True}


class VerificationLetterNotSentTestView(BaseTestView):
    @property
    def company_profile(self):
        return {'is_verification_letter_sent': False}


class IsCompanyOwnerTestView(BaseTestView):
    @property
    def supplier_profile(self):
        return {'is_company_owner': True}


class NotCompanyOwnerTestView(BaseTestView):
    @property
    def supplier_profile(self):
        return {'is_company_owner': False}


def create_view_for_rule(rule_class, ViewClass=BaseTestView):
    class TestView(redirects.RedirectRuleHandlerMixin, ViewClass):
        redirect_rules = [rule_class]
    return TestView.as_view()


def test_redirect_rule_handler_mixin_provides_context():
    pass


def test_redirect_rule_handler_mixin_redirect_required(rf):
    class RedirectRequired(redirects.RedirectRule):
        url = '/some/url'

        def is_redirect_required(self):
            return True

    view = create_view_for_rule(RedirectRequired, BaseTestView)
    response = view(rf.get('/'))

    assert response.status_code == 302
    assert response.url == '/some/url'


def test_redirect_rule_handler_mixin_redirect_not_required(rf):
    class RedirectNotRequired(redirects.RedirectRule):
        url = '/some/url'

        def is_redirect_required(self):
            return False

    view = create_view_for_rule(RedirectNotRequired)
    response = view(rf.get('/'))

    assert response.status_code == 200


def test_is_logged_in_rule_anon_user(rf):
    request = rf.get('/')
    request.sso_user = None

    view = create_view_for_rule(redirects.IsLoggedInRule)
    response = view(request)

    assert response.status_code == 302
    assert response.url == (
        'http://sso.trade.great:8004/accounts/login/?next=http%3A//testserver/'
    )


def test_is_logged_in_rule_authed_user(rf):
    request = rf.get('/')
    request.sso_user = Mock()
    view = create_view_for_rule(redirects.IsLoggedInRule)
    response = view(request)

    assert response.status_code == 200


def test_company_required_rule_has_company(rf):
    view = create_view_for_rule(
        redirects.CompanyRequiredRule, CompanyTestView
    )
    response = view(rf.get('/'))

    assert response.status_code == 200


def test_company_required_rule_no_company(rf):
    view = create_view_for_rule(
        redirects.CompanyRequiredRule, NoCompanyTestView
    )
    response = view(rf.get('/'))

    assert response.status_code == 302
    assert response.url == reverse('index')


def test_no_company_required_rule_has_company(rf):
    view = create_view_for_rule(
        redirects.NoCompanyRequiredRule, CompanyTestView
    )
    response = view(rf.get('/'))

    assert response.status_code == 302
    assert response.url == reverse('company-detail')


def test_no_company_required_rule_no_company(rf):
    view = create_view_for_rule(
        redirects.NoCompanyRequiredRule, NoCompanyTestView
    )
    response = view(rf.get('/'))

    assert response.status_code == 200


def test_unverified_company_required_is_verified(rf):
    view = create_view_for_rule(
        redirects.UnverifiedCompanyRequiredRule,
        VerifiedCompanyTestView
    )
    response = view(rf.get('/'))

    assert response.status_code == 302
    assert response.url == reverse('company-detail')


def test_unverified_company_required_is_unverified(rf):
    view = create_view_for_rule(
        redirects.UnverifiedCompanyRequiredRule,
        UnverifiedCompanyTestView
    )
    response = view(rf.get('/'))

    assert response.status_code == 200


def test_verification_letter_not_sent_is_sent(rf):
    view = create_view_for_rule(
        redirects.VerificationLetterNotSentRequiredRule,
        VerificationLetterSentTestView
    )
    response = view(rf.get('/'))

    assert response.status_code == 302
    assert response.url == reverse('verify-company-address-confirm')


def test_verification_letter_no_sent_is_not_sent(rf):
    view = create_view_for_rule(
        redirects.VerificationLetterNotSentRequiredRule,
        VerificationLetterNotSentTestView
    )
    response = view(rf.get('/'))

    assert response.status_code == 200


def test_company_owner_required_is_company_owner(rf):
    view = create_view_for_rule(
        redirects.CompanyOwnerRequiredRule,
        IsCompanyOwnerTestView
    )
    response = view(rf.get('/'))

    assert response.status_code == 200


def test_company_owner_required_not_company_owner(rf):
    view = create_view_for_rule(
        redirects.CompanyOwnerRequiredRule,
        NotCompanyOwnerTestView
    )
    response = view(rf.get('/'))

    assert response.status_code == 302
    assert response.url == reverse('company-detail')


def test_not_company_owner_required_is_company_owner(rf):
    view = create_view_for_rule(
        redirects.NotCompanyOwnerRequiredRule,
        IsCompanyOwnerTestView
    )
    response = view(rf.get('/'))

    assert response.status_code == 302
    assert response.url == reverse('company-detail')


def test_not_company_owner_required_not_company_owner(rf):
    view = create_view_for_rule(
        redirects.NotCompanyOwnerRequiredRule,
        NotCompanyOwnerTestView
    )
    response = view(rf.get('/'))

    assert response.status_code == 200
