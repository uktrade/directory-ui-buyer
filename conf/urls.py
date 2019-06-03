import conf.sitemaps

import directory_healthcheck.views
import directory_components.views
from directory_constants.urls import build_great_url

from django.conf.urls import include, url
from django.contrib.sitemaps.views import sitemap
from django.views.decorators.http import require_http_methods
from django.views.generic import RedirectView

import company.views
import enrolment.views
import proxy.views


sitemaps = {
    'static': conf.sitemaps.StaticViewSitemap,
}


require_get = require_http_methods(['GET'])


healthcheck_urls = [
    url(
        r'^$',
        directory_healthcheck.views.HealthcheckView.as_view(),
        name='healthcheck'
    ),
]


api_urls = [
    url(
        r'^api/external(?P<path>/supplier/company/)$',
        require_get(proxy.views.APIViewProxy.as_view()),
        name='external-company'
    ),
    url(
        r'^api/external(?P<path>/healthcheck/ping/)$',
        require_get(proxy.views.APIViewProxy.as_view()),
        name='external-ping'
    ),
    url(
        r'^api(?P<path>/external/supplier/)$',
        require_get(proxy.views.APIViewProxy.as_view()),
        name='external-supplier'
    ),
    url(
        r'^api(?P<path>/external/supplier-sso/)$',
        require_get(proxy.views.APIViewProxy.as_view()),
        name='external-supplier-sso'
    ),
    url(
        r'^directory-api(?P<path>)',
        proxy.views.DirectoryAPIViewProxy.as_view(),
        name='directory-api'
    ),
]


urlpatterns = [
    url(
        r'^healthcheck/',
        include(
            healthcheck_urls, namespace='healthcheck', app_name='healthcheck'
        )
    ),
    url(
        r'^',
        include(api_urls, namespace='api', app_name='api')
    ),
    url(
        r"^robots\.txt$",
        directory_components.views.RobotsView.as_view(),
        name='robots'
    ),
    url(
        r"^sitemap\.xml$", sitemap, {'sitemaps': sitemaps},
        name='sitemap'
    ),
    url(
        r'^$',
        enrolment.views.DomesticLandingView.as_view(),
        name='index'
    ),
    url(
        r'^unsubscribe/',
        company.views.EmailUnsubscribeView.as_view(),
        name='unsubscribe'
    ),

    url(
        r'^verify/$',
        company.views.CompanyVerifyView.as_view(),
        name='verify-company-hub'
    ),
    url(
        r'^verify/letter-send/$',
        company.views.SendVerificationLetterView.as_view(),
        name='verify-company-address'
    ),
    url(
        r'^verify/letter-confirm/$',
        company.views.CompanyAddressVerificationView.as_view(),
        name='verify-company-address-confirm'
    ),
    url(
        r'^verify/companies-house/$',
        company.views.CompaniesHouseOauth2View.as_view(),
        name='verify-companies-house'
    ),
    url(
        r'^companies-house-oauth2-callback/$',
        company.views.CompaniesHouseOauth2CallbackView.as_view(),
        name='verify-companies-house-callback'
    ),
    url(
        r'^confirm-company-address/$',
        company.views.CompanyAddressVerificationHistoricView.as_view(),
        name='verify-company-address-historic-url'
    ),
    url(
        r'^account/add-collaborator/$',
        company.views.AddCollaboratorView.as_view(),
        name='add-collaborator'
    ),
    url(
        r'^account/remove-collaborator/$',
        company.views.RemoveCollaboratorView.as_view(),
        name='remove-collaborator'
    ),
    url(
        r'^account/transfer/$',
        company.views.TransferAccountWizardView.as_view(),
        name='account-transfer'
    ),
    url(
        r'^account/transfer/accept/$',
        company.views.AcceptTransferAccountView.as_view(),
        name='account-transfer-accept'
    ),
    url(
        r'^account/collaborate/accept/$',
        company.views.AcceptCollaborationView.as_view(),
        name='account-collaborate-accept'
    ),
    # the url to create case studies was ../edit/. That was bad naming.
    url(
        r'^data-science/buyers/$',
        company.views.BuyerCSVDumpView.as_view(),
        name='buyers-csv-dump'
    ),
    url(
        r'^data-science/suppliers/$',
        company.views.SupplierCSVDumpView.as_view(),
        name='suppliers-csv-dump'
    )
]

urlpatterns += [
    url(
        r'^register/(?P<step>.+)/$',
        RedirectView.as_view(url=build_great_url('profile/enrol/')),
    ),
    url(
        r'^register-submit/$',
        RedirectView.as_view(url=build_great_url('profile/enrol/')),
    ),
    url(
        r'^company-profile/$',
        RedirectView.as_view(url=build_great_url('profile/find-a-buyer/')),
        name='company-detail',
    ),
    url(
        r'^company-profile/edit/$',
        RedirectView.as_view(url=build_great_url('profile/find-a-buyer/'))
    ),
    url(
        r'^company-profile/edit/logo/$',
        RedirectView.as_view(url=build_great_url('profile/find-a-buyer/')),
    ),
    url(
        r'^company-profile/edit/description/$',
        RedirectView.as_view(url=build_great_url('profile/find-a-buyer/')),
    ),
    url(
        r'^company-profile/edit/key-facts/$',
        RedirectView.as_view(url=build_great_url('profile/find-a-buyer/'))
    ),
    url(
        r'^company-profile/edit/sectors/$',
        RedirectView.as_view(url=build_great_url('profile/find-a-buyer/')),
    ),
    url(
        r'^company-profile/edit/contact/$',
        RedirectView.as_view(url=build_great_url('profile/find-a-buyer/')),
    ),
    url(
        r'^company-profile/edit/address/$',
        RedirectView.as_view(url=build_great_url('profile/find-a-buyer/')),
    ),
    url(
        r'^company-profile/edit/social-media/$',
        RedirectView.as_view(url=build_great_url('profile/find-a-buyer/'))
    ),
    url(
        r'^company/case-study/create/$',
        RedirectView.as_view(url=build_great_url('profile/find-a-buyer/')),
        name='company-case-study-create',
    ),
    url(
        r'^company/case-study/edit/(?P<id>[0-9]+)/$',
        RedirectView.as_view(url=build_great_url('profile/find-a-buyer/')),
    ),
    url(
        r'^company/case-study/edit/$',
        RedirectView.as_view(url=build_great_url('profile/find-a-buyer/')),
        name='company-case-study-create-backwards-compatible',
    ),
    url(
        r'^register$',
        RedirectView.as_view(url=build_great_url('profile/enrol/')),
        name='register',
    ),
]

urlpatterns = [
    url(
        r'^find-a-buyer/',
        include(urlpatterns)
    ),
]
