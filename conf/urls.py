import directory_components.views
import conf.sitemaps

from django.conf.urls import url
from django.contrib.sitemaps.views import sitemap
from django.views.decorators.http import require_http_methods
from django.views.generic import RedirectView

import company.views
import enrolment.views
import healthcheck.views
import proxy.views


sitemaps = {
    'static': conf.sitemaps.StaticViewSitemap,
}


require_get = require_http_methods(['GET'])


urlpatterns = [
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
        r'^healthcheck/api/$',
        healthcheck.views.APICheckAPIView.as_view(),
        name='healthcheck-api'
    ),
    url(
        r'^healthcheck/single-sign-on/$',
        healthcheck.views.SingleSignOnAPIView.as_view(),
        name='healthcheck-single-sign-on'
    ),
    url(
        r'^$',
        enrolment.views.DomesticLandingView.as_view(),
        name='index'
    ),
    url(
        r'^register/(?P<step>.+)/$',
        enrolment.views.EnrolmentView.as_view(
            url_name='register', done_step_name='finished'
        ),
        name='register'
    ),
    url(
        r'^register-submit/$',
        enrolment.views.SubmitEnrolmentView.as_view(),
        name='register-submit'
    ),
    url(
        r'^company-profile/$',
        company.views.CompanyProfileDetailView.as_view(),
        name='company-detail'
    ),
    url(
        r'^company-profile/edit/$',
        company.views.CompanyProfileEditView.as_view(),
        name='company-edit'
    ),
    url(
        r'^company-profile/edit/logo/$',
        company.views.CompanyProfileLogoEditView.as_view(),
        name='company-edit-logo'
    ),
    url(
        r'^company-profile/edit/description/$',
        company.views.CompanyDescriptionEditView.as_view(),
        name='company-edit-description'
    ),
    url(
        r'^company-profile/edit/key-facts/$',
        company.views.SupplierBasicInfoEditView.as_view(),
        name='company-edit-key-facts'
    ),
    url(
        r'^company-profile/edit/sectors/$',
        company.views.SupplierClassificationEditView.as_view(),
        name='company-edit-sectors'
    ),
    url(
        r'^company-profile/edit/contact/$',
        company.views.SupplierContactEditView.as_view(),
        name='company-edit-contact'
    ),
    url(
        r'^company-profile/edit/address/$',
        company.views.SupplierAddressEditView.as_view(),
        name='company-edit-address'
    ),
    url(
        r'^company-profile/edit/social-media/$',
        company.views.CompanySocialLinksEditView.as_view(),
        name='company-edit-social-media'
    ),
    url(
        r'^company/case-study/create/$',
        company.views.SupplierCaseStudyWizardView.as_view(),
        name='company-case-study-create'
    ),
    url(
        r'^company/case-study/edit/(?P<id>[0-9]+)/$',
        company.views.SupplierCaseStudyWizardView.as_view(),
        name='company-case-study-edit'
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
    url(
        r'^api/external(?P<path>/supplier/company/)$',
        require_get(proxy.views.APIViewProxy.as_view()),
        name='api-external-company'
    ),
    url(
        r'^api/external(?P<path>/healthcheck/ping/)$',
        require_get(proxy.views.APIViewProxy.as_view()),
        name='api-external-ping'
    ),
    url(
        r'^api(?P<path>/external/supplier/)$',
        require_get(proxy.views.APIViewProxy.as_view()),
        name='api-external-supplier'
    ),
    url(
        r'^api(?P<path>/external/supplier-sso/)$',
        require_get(proxy.views.APIViewProxy.as_view()),
        name='api-external-supplier-sso'
    ),
    url(
        r'^api/internal/companies-house-search/$',
        enrolment.views.CompaniesHouseSearchApiView.as_view(),
        name='api-internal-companies-house-search'
    ),
    url(
        r'^directory-api(?P<path>)',
        proxy.views.DirectoryAPIViewProxy.as_view(),
        name='directory-api'
    ),
    url(
        r'^errors/image-too-large/$',
        company.views.RequestPaylodTooLargeErrorView.as_view(),
        name='request-payload-too-large'
    ),
    # first step of enrolment was /register. It's moved to the landing page
    url(
        r'^register$',
        RedirectView.as_view(pattern_name='index'),
    ),

    # the url to create case studies was ../edit/. That was bad naming.
    url(
        r'^company/case-study/edit/$',
        RedirectView.as_view(pattern_name='company-case-study-create'),
        name='company-case-study-create-backwards-compatible'
    ),
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
