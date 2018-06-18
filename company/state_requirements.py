import abc

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse_lazy

from sso.utils import build_url_with_next


class UserStateRule(abc.ABC):

    def __init__(self, context):
        self.context = context

    @abc.abstractmethod
    def handle_invalid_state(self):
        """
        Return a HttpResponse due to the user not being in the required state.

        """

    @abc.abstractmethod
    def is_user_in_required_state(self):
        pass


class RedirectUserStateRule(UserStateRule):

    @property
    def redirect_url(self):
        """ The url to redirect to"""

    def handle_invalid_state(self):
        return redirect(self.redirect_url)


class UserStateRequirementHandlerMixin:

    required_user_states = []

    def dispatch(self, *args, **kwargs):
        for rule_class in self.required_user_states:
            rule = rule_class(context={'request': self.request, 'view': self})
            if not rule.is_user_in_required_state():
                return rule.handle_invalid_state()
        return super().dispatch(*args, **kwargs)


class IsLoggedIn(RedirectUserStateRule):

    @property
    def redirect_url(self):
        return build_url_with_next(
            redirect_url=settings.SSO_PROXY_LOGIN_URL,
            next_url=self.context['request'].build_absolute_uri(),
        )

    def is_user_in_required_state(self):
        return self.context['request'].sso_user is not None


class HasCompany(RedirectUserStateRule):

    redirect_url = reverse_lazy('index')

    def is_user_in_required_state(self):
        return bool(self.context['view'].company_profile)


class NoCompany(RedirectUserStateRule):

    redirect_url = reverse_lazy('company-detail')

    def is_user_in_required_state(self):
        return not self.context['view'].company_profile


class HasUnverifiedCompany(RedirectUserStateRule):

    redirect_url = reverse_lazy('company-detail')

    def is_user_in_required_state(self):
        profile = self.context['view'].company_profile
        return profile and not profile['is_verified']


class VerificationLetterNotSent(RedirectUserStateRule):

    redirect_url = reverse_lazy('verify-company-address-confirm')

    def is_user_in_required_state(self):
        profile = self.context['view'].company_profile
        return not profile['is_verification_letter_sent']


class IsCompanyOwner(RedirectUserStateRule):

    redirect_url = reverse_lazy('company-detail')

    def is_user_in_required_state(self):
        profile = self.context['view'].supplier_profile
        return profile and profile['is_company_owner']


class NotCompanyOwner(RedirectUserStateRule):

    redirect_url = reverse_lazy('company-detail')

    def is_user_in_required_state(self):
        profile = self.context['view'].supplier_profile
        return not profile['is_company_owner'] if profile else True
