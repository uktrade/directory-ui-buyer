from django.conf.urls import url
from django.views.decorators.cache import cache_page

from enrolment.views import (
    DomesticLandingView,
    EnrolmentInstructionsView,
    EnrolmentView,
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
    EmailUnsubscribeView
)
from admin.proxy import AdminProxyView


cache_me = cache_page(60 * 1)


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
        r'^register$',
        EnrolmentInstructionsView.as_view(),
        name='register-instructions'
    ),
    url(
        r'^register/(?P<step>.+)$',
        EnrolmentView.as_view(url_name='register', done_step_name='finished'),
        name='register'
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
]
