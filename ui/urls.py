from django.conf.urls import url
from django.views.decorators.http import require_http_methods
from django.views.generic import RedirectView, TemplateView

from enrolment.views import (
    CompaniesHouseSearchApiView,
    DomesticLandingView,
    EnrolmentView,
    SubmitEnrolmentView,
)
from company.views import (
    SupplierAddressEditView,
    SupplierBasicInfoEditView,
    SupplierCaseStudyWizardView,
    SupplierClassificationEditView,
    SupplierCompanyAddressVerificationView,
    SupplierCompanyDescriptionEditView,
    SupplierCompanyProfileDetailView,
    SupplierCompanyProfileEditView,
    SupplierCompanyProfileLogoEditView,
    SupplierCompanySocialLinksEditView,
    SupplierContactEditView,
    EmailUnsubscribeView,
    RequestPaylodTooLargeErrorView,
)
from company import proxy as company_proxies
from admin.proxy import AdminProxyView


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
        name='admin_proxy'
    ),
    url(
        r'^$',
        DomesticLandingView.as_view(),
        name='index'
    ),
    url(
        r'^register/(?P<step>.+)$',
        EnrolmentView.as_view(url_name='register', done_step_name='finished'),
        name='register'
    ),
    url(
        r'^register-submit$',
        SubmitEnrolmentView.as_view(),
        name='register-submit'
    ),
    url(
        r'^confirm-company-address$',
        SupplierCompanyAddressVerificationView.as_view(),
        name='confirm-company-address'
    ),
    url(
        r'^company-profile$',
        SupplierCompanyProfileDetailView.as_view(),
        name='company-detail'
    ),
    url(
        r'^company-profile/edit$',
        SupplierCompanyProfileEditView.as_view(),
        name='company-edit'
    ),
    url(
        r'^company-profile/edit/logo$',
        SupplierCompanyProfileLogoEditView.as_view(),
        name='company-edit-logo'
    ),
    url(
        r'^company-profile/edit/description$',
        SupplierCompanyDescriptionEditView.as_view(),
        name='company-edit-description'
    ),
    url(
        r'^company-profile/edit/key-facts$',
        SupplierBasicInfoEditView.as_view(),
        name='company-edit-key-facts'
    ),
    url(
        r'^company-profile/edit/sectors$',
        SupplierClassificationEditView.as_view(),
        name='company-edit-sectors'
    ),
    url(
        r'^company-profile/edit/contact$',
        SupplierContactEditView.as_view(),
        name='company-edit-contact'
    ),
    url(
        r'^company-profile/edit/address$',
        SupplierAddressEditView.as_view(),
        name='company-edit-address'
    ),
    url(
        r'^company-profile/edit/social-media$',
        SupplierCompanySocialLinksEditView.as_view(),
        name='company-edit-social-media'
    ),
    url(
        r'^company/case-study/edit/(?P<id>.+)?$',
        SupplierCaseStudyWizardView.as_view(),
        name='company-case-study-edit'
    ),
    url(
        r'^unsubscribe/',
        EmailUnsubscribeView.as_view(),
        name='unsubscribe'
    ),
    url(
        r'^api/external/supplier/company/$',
        require_get(company_proxies.APIViewProxy.as_view()),
        name='api-external-company'
    ),
    url(
        r'^api/external/supplier/$',
        require_get(company_proxies.APIViewProxy.as_view()),
        name='api-external-supplier'
    ),
    url(
        r'^api/external/supplier-sso/$',
        require_get(company_proxies.APIViewProxy.as_view()),
        name='api-external-supplier'
    ),
    url(
        r'^api/internal/companies-house-search/$',
        CompaniesHouseSearchApiView.as_view(),
        name='api-internal-companies-house-search'
    ),

    url(
        r'^errors/image-too-large/$',
        RequestPaylodTooLargeErrorView.as_view(),
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
]
