from django.conf.urls import url
from django.views.decorators.http import require_http_methods
from django.views.generic import RedirectView, TemplateView

from admin.proxy import AdminProxyView
from company import views as company_views
from enrolment import views as enrolment_views
import healthcheck.views
from proxy.views import APIViewProxy, DirectoryAPIViewProxy


require_get = require_http_methods(['GET'])


urlpatterns = [
    url(
        r'^admin/',
        AdminProxyView.as_view(),
        name='admin_proxy'
    ),
    url(
        r'^api-static/admin/',
        AdminProxyView.as_view(),
        name='admin_proxy_static'
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
        enrolment_views.DomesticLandingView.as_view(),
        name='index'
    ),
    url(
        r'^register/(?P<step>.+)/$',
        enrolment_views.EnrolmentView.as_view(
            url_name='register', done_step_name='finished'
        ),
        name='register'
    ),
    url(
        r'^register-submit/$',
        enrolment_views.SubmitEnrolmentView.as_view(),
        name='register-submit'
    ),
    url(
        r'^company-profile/$',
        company_views.CompanyProfileDetailView.as_view(),
        name='company-detail'
    ),
    url(
        r'^company-profile/edit/$',
        company_views.CompanyProfileEditView.as_view(),
        name='company-edit'
    ),
    url(
        r'^company-profile/edit/logo/$',
        company_views.CompanyProfileLogoEditView.as_view(),
        name='company-edit-logo'
    ),
    url(
        r'^company-profile/edit/description/$',
        company_views.CompanyDescriptionEditView.as_view(),
        name='company-edit-description'
    ),
    url(
        r'^company-profile/edit/key-facts/$',
        company_views.SupplierBasicInfoEditView.as_view(),
        name='company-edit-key-facts'
    ),
    url(
        r'^company-profile/edit/sectors/$',
        company_views.SupplierClassificationEditView.as_view(),
        name='company-edit-sectors'
    ),
    url(
        r'^company-profile/edit/contact/$',
        company_views.SupplierContactEditView.as_view(),
        name='company-edit-contact'
    ),
    url(
        r'^company-profile/edit/address/$',
        company_views.SupplierAddressEditView.as_view(),
        name='company-edit-address'
    ),
    url(
        r'^company-profile/edit/social-media/$',
        company_views.CompanySocialLinksEditView.as_view(),
        name='company-edit-social-media'
    ),
    url(
        r'^company/case-study/create/$',
        company_views.SupplierCaseStudyWizardView.as_view(),
        name='company-case-study-create'
    ),
    url(
        r'^company/case-study/edit/(?P<id>[0-9]+)/$',
        company_views.SupplierCaseStudyWizardView.as_view(),
        name='company-case-study-edit'
    ),
    url(
        r'^unsubscribe/',
        company_views.EmailUnsubscribeView.as_view(),
        name='unsubscribe'
    ),

    url(
        r'^verify/$',
        company_views.CompanyVerifyView.as_view(),
        name='verify-company-hub'
    ),
    url(
        r'^verify/letter-send/$',
        company_views.SendVerificationLetterView.as_view(),
        name='verify-company-address'
    ),
    url(
        r'^verify/letter-confirm/$',
        company_views.CompanyAddressVerificationView.as_view(),
        name='verify-company-address-confirm'
    ),
    url(
        r'^verify/companies-house/$',
        company_views.CompaniesHouseOauth2View.as_view(),
        name='verify-companies-house'
    ),
    url(
        r'^companies-house-oauth2-callback/$',
        company_views.CompaniesHouseOauth2CallbackView.as_view(),
        name='verify-companies-house-callback'
    ),
    url(
        r'^confirm-company-address/$',
        company_views.CompanyAddressVerificationHistoricView.as_view(),
        name='verify-company-address-historic-url'
    ),
    url(
        r'^account/add-collaborator/$',
        company_views.AddCollaboratorView.as_view(),
        name='add-collaborator'
    ),
    url(
        r'^account/remove-collaborator/$',
        company_views.RemoveCollaboratorView.as_view(),
        name='remove-collaborator'
    ),
    url(
        r'^account/transfer/$',
        company_views.TransferAccountWizardView.as_view(),
        name='account-transfer'
    ),
    url(
        r'^account/transfer/accept/$',
        company_views.AcceptTransferAccountView.as_view(),
        name='account-transfer-accept'
    ),

    url(
        r'^account/collaborate/accept/$',
        company_views.AcceptCollaborationView.as_view(),
        name='account-collaborate-accept'
    ),
    url(
        r'^api/external(?P<path>/supplier/company/)$',
        require_get(APIViewProxy.as_view()),
        name='api-external-company'
    ),
    url(
        r'^api/external(?P<path>/healthcheck/ping/)$',
        require_get(APIViewProxy.as_view()),
        name='api-external-ping'
    ),
    url(
        r'^api(?P<path>/external/supplier/)$',
        require_get(APIViewProxy.as_view()),
        name='api-external-supplier'
    ),
    url(
        r'^api(?P<path>/external/supplier-sso/)$',
        require_get(APIViewProxy.as_view()),
        name='api-external-supplier-sso'
    ),
    url(
        r'^api/internal/companies-house-search/$',
        enrolment_views.CompaniesHouseSearchApiView.as_view(),
        name='api-internal-companies-house-search'
    ),
    url(
        r'^directory-api(?P<path>)',
        DirectoryAPIViewProxy.as_view(),
        name='directory-api'
    ),
    url(
        r'^errors/image-too-large/$',
        company_views.RequestPaylodTooLargeErrorView.as_view(),
        name='request-payload-too-large'
    ),
    url(
        r"^robots\.txt$",
        TemplateView.as_view(
            template_name='robots.txt', content_type='text/plain'
        ),
        name='robots'
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
]
