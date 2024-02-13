import conf.sitemaps

import directory_healthcheck.views
import directory_components.views
from directory_components.decorators import skip_ga360
from directory_constants.urls import domestic

from django.urls import reverse_lazy, re_path
from django.conf.urls import include
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.contrib.sitemaps.views import sitemap
from django.views.decorators.http import require_http_methods
from django.views.generic import RedirectView

import company.views
import enrolment.views


sitemaps = {
    'static': conf.sitemaps.StaticViewSitemap,
}


require_get = require_http_methods(['GET'])


def company_required(function):
    inner = user_passes_test(
        lambda user: bool(user.company),
        reverse_lazy('index'),
        None
    )
    return login_required(inner(function))


def no_company_required(function):
    inner = user_passes_test(
        lambda user: not bool(user.company),
        domestic.FIND_A_BUYER,
        None
    )
    return login_required(inner(function))


def owner_required(function):
    inner = user_passes_test(
        lambda user: user.supplier.get('is_company_owner', False),
        domestic.FIND_A_BUYER,
        None
    )
    return company_required(inner(function))


def not_owner_required(function):
    inner = user_passes_test(
        lambda user: not user.supplier.get('is_company_owner', False),
        domestic.FIND_A_BUYER,
        None,
    )
    return login_required(inner(function))


def unverified_required(function):
    inner = user_passes_test(
        lambda user: not user.company['is_verified'],
        domestic.FIND_A_BUYER,
        None
    )
    return company_required(inner(function))


def no_letter_required(function):
    inner = user_passes_test(
        lambda user: not user.company['is_verification_letter_sent'],
        reverse_lazy('verify-company-address-confirm'),
        None
    )
    return unverified_required(inner(function))


healthcheck_urls = [
    re_path(
        r'^$',
        skip_ga360(directory_healthcheck.views.HealthcheckView.as_view()),
        name='healthcheck'
    ),
]


urlpatterns = [
    re_path(r'^healthcheck/', include((healthcheck_urls, 'healthcheck'), namespace='healthcheck')),
    re_path(
        r"^robots\.txt$",
        skip_ga360(directory_components.views.RobotsView.as_view()),
        name='robots'
    ),
    re_path(
        r"^sitemap\.xml$", sitemap, {'sitemaps': sitemaps},
        name='sitemap'
    ),
    re_path(
        r'^unsubscribe/',
        login_required(company.views.EmailUnsubscribeView.as_view()),
        name='unsubscribe'
    ),
    re_path(
        r'^verify/$',
        no_letter_required(company.views.CompanyVerifyView.as_view()),
        name='verify-company-hub'
    ),
    re_path(
        r'^verify/letter-send/$',
        no_letter_required(company.views.SendVerificationLetterView.as_view()),
        name='verify-company-address'
    ),
    re_path(
        r'^verify/letter-confirm/$',
        unverified_required(company.views.CompanyAddressVerificationView.as_view()),
        name='verify-company-address-confirm'
    ),
    re_path(
        r'^verify/companies-house/$',
        unverified_required(company.views.CompaniesHouseOauth2View.as_view()),
        name='verify-companies-house'
    ),
    re_path(
        r'^companies-house-oauth2-callback/$',
        unverified_required(company.views.CompaniesHouseOauth2CallbackView.as_view()),
        name='verify-companies-house-callback'
    ),
    re_path(
        r'^confirm-company-address/$',
        company.views.CompanyAddressVerificationHistoricView.as_view(),
        name='verify-company-address-historic-url'
    ),
    # the url to create case studies was ../edit/. That was bad naming.
    re_path(
        r'^data-science/buyers/$',
        skip_ga360(company.views.BuyerCSVDumpView.as_view()),
        name='buyers-csv-dump'
    ),
    re_path(
        r'^data-science/suppliers/$',
        skip_ga360(company.views.SupplierCSVDumpView.as_view()),
        name='suppliers-csv-dump'
    )
]

urlpatterns += [
    re_path(
        r'^register/(?P<step>.+)/$',
        RedirectView.as_view(url=domestic.SINGLE_SIGN_ON_PROFILE / 'enrol/'),
    ),
    re_path(
        r'^register-submit/$',
        RedirectView.as_view(url=domestic.SINGLE_SIGN_ON_PROFILE / 'enrol/'),
    ),
    re_path(
        r'^company-profile/$',
        RedirectView.as_view(url=domestic.SINGLE_SIGN_ON_PROFILE),
        name='company-detail',
    ),
    re_path(
        r'^company-profile/edit/$',
        RedirectView.as_view(url=domestic.SINGLE_SIGN_ON_PROFILE)
    ),
    re_path(
        r'^company-profile/edit/logo/$',
        RedirectView.as_view(url=domestic.SINGLE_SIGN_ON_PROFILE),
    ),
    re_path(
        r'^company-profile/edit/description/$',
        RedirectView.as_view(url=domestic.SINGLE_SIGN_ON_PROFILE),
    ),
    re_path(
        r'^company-profile/edit/key-facts/$',
        RedirectView.as_view(url=domestic.SINGLE_SIGN_ON_PROFILE)
    ),
    re_path(
        r'^company-profile/edit/sectors/$',
        RedirectView.as_view(url=domestic.SINGLE_SIGN_ON_PROFILE),
    ),
    re_path(
        r'^company-profile/edit/contact/$',
        RedirectView.as_view(url=domestic.SINGLE_SIGN_ON_PROFILE),
    ),
    re_path(
        r'^company-profile/edit/address/$',
        RedirectView.as_view(url=domestic.SINGLE_SIGN_ON_PROFILE),
    ),
    re_path(
        r'^company-profile/edit/social-media/$',
        RedirectView.as_view(url=domestic.SINGLE_SIGN_ON_PROFILE)
    ),
    re_path(
        r'^company/case-study/create/$',
        RedirectView.as_view(url=domestic.SINGLE_SIGN_ON_PROFILE),
        name='company-case-study-create',
    ),
    re_path(
        r'^company/case-study/edit/(?P<id>[0-9]+)/$',
        RedirectView.as_view(url=domestic.SINGLE_SIGN_ON_PROFILE),
    ),
    re_path(
        r'^company/case-study/edit/$',
        RedirectView.as_view(url=domestic.SINGLE_SIGN_ON_PROFILE),
        name='company-case-study-create-backwards-compatible',
    ),
    re_path(
        r'^register$',
        RedirectView.as_view(url=domestic.SINGLE_SIGN_ON_PROFILE / 'enrol/'),
        name='register',
    ),
]

urlpatterns = [
    re_path(r'^find-a-buyer/', include(urlpatterns)),
]
