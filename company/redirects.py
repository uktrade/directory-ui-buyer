import abc

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse_lazy

from sso.utils import build_url_with_next


class RedirectRule(abc.ABC):

    def __init__(self, context):
        self.context = context

    @property
    @abc.abstractmethod
    def url(self):
        """ The url to redirect to"""
        pass

    @abc.abstractmethod
    def is_redirect_required(self):
        """Return True if the user should be redirected to `url`"""
        pass


class RedirectRuleHandlerMixin:

    redirect_rules = []

    def dispatch(self, *args, **kwargs):
        for rule_class in self.redirect_rules:
            rule = rule_class(context={'request': self.request, 'view': self})
            if rule.is_redirect_required():
                return redirect(rule.url)
        return super().dispatch(*args, **kwargs)


class IsLoggedInRule(RedirectRule):

    @property
    def url(self):
        return build_url_with_next(
            redirect_url=settings.SSO_PROXY_LOGIN_URL,
            next_url=self.context['request'].build_absolute_uri(),
        )

    def is_redirect_required(self):
        return self.context['request'].sso_user is None


class CompanyRequiredRule(RedirectRule):

    url = reverse_lazy('index')

    def is_redirect_required(self):
        return not self.context['view'].company_profile


class NoCompanyRequiredRule(RedirectRule):

    url = reverse_lazy('company-detail')

    def is_redirect_required(self):
        return bool(self.context['view'].company_profile)


class UnverifiedCompanyRequiredRule(RedirectRule):

    url = reverse_lazy('company-detail')

    def is_redirect_required(self):
        profile = self.context['view'].company_profile
        return profile and profile['is_verified']


class VerificationLetterNotSentRequiredRule(RedirectRule):

    url = reverse_lazy('verify-company-address-confirm')

    def is_redirect_required(self):
        profile = self.context['view'].company_profile
        return profile['is_verification_letter_sent']


class CompanyOwnerRequiredRule(RedirectRule):

    url = reverse_lazy('company-detail')

    def is_redirect_required(self):
        profile = self.context['view'].supplier_profile
        return not profile or not profile['is_company_owner']


class NotCompanyOwnerRequiredRule(RedirectRule):

    url = reverse_lazy('company-detail')

    def is_redirect_required(self):
        profile = self.context['view'].supplier_profile
        return profile['is_company_owner'] if profile else False
