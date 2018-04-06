import abc

from django.conf import settings

from api_client import api_client
from sso.utils import SSOLoginRequiredMixin, build_sso_url


class RedirectRule(abc.ABC):

    def __init__(self, request, company_profile, supplier_profile):
        self.request = request
        self.company_profile = company_profile

    @property
    @abc.abstractmethod
    def login_required(self):
       """True if the user must be logged in"""
       pass

    @property
    @abstractmethod
    def url(self):
       """ The url to redirect to"""
       pass

    @abc.abstractmethod
    def object_meets_criteria(self):
        """Return True if the user should be redirected to `url`"""
        pass


class RedirectRulehandlerMixin:
    redirect_rules = []
    def dispatch(self, *args, **kwargs):
        for Rule in self.redirect_rules:
            rule = Rule(
                request=self.request,
                company_profile=self.company_profile,
            )
            if rule.object_meets_criteria():
                return redirect(rule.url)
        return super().dispatch(*args, **kwargs)


class IsLoggedInRule(RedirectRule):
    @property
    def url(self):
        return build_sso_url(
            redirect_url=settings.SSO_PROXY_LOGIN_URL,
            next_url=self.request.build_absolute_uri(),
        )

    def object_meets_criteria(self):
        return self.request.sso_user is None


class CompanyRequiredRule(RedirectRule):

    url = reverse_lazy('index')

    def object_meets_criteria(self):
        return not self.company_profile


class NoCompanyRequiredRule(RedirectRule):

    url = reverse_lazy('company-detail')

    def object_meets_criteria(self):
        return bool(self.company_profile)


class UnverifiedCompanyRequiredRule(RedirectRule):

    url = reverse_lazy('company-detail')

    def object_meets_criteria(self):
        profile = self.company_profile
        return profile and profile['is_verified']


class VerificationLetterNotSentRequiredRule(RedirectRule):

    url = reverse_lazy('verify-company-address-confirm')

    def object_meets_criteria(self):
        return self.company_profile['is_verification_letter_sent']


class SupplierProfileMixin:
    @property
    def supplier_profile(self):
        response = api_client.supplier.retrieve_profile(
            sso_session_id=self.request.sso_user.session_id,
        )
        if response.status_code == 404:
            return {}
        response.raise_for_status()
        return response.json()


class CompanyOwnerRequiredRule(SupplierProfileMixin, RedirectRule):

    url = reverse_lazy('company-detail')

    def object_meets_criteria(self):
        profile = self.supplier_profile
        return not profile or not profile['is_company_owner']


class NotCompanyOwnerRequiredRule(SupplierProfileMixin, RedirectRule):

    url = reverse_lazy('company-detail')

    def object_meets_criteria(self):
        profile = self.supplier_profile
        return not profile or profile['is_company_owner']



