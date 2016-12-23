from django.conf.urls import url
from django.conf import settings
from django.views.decorators.cache import cache_page

from enrolment.views import (
    CachableTemplateView,
    DomesticLandingView,
    EnrolmentInstructionsView,
    EnrolmentView,
    InternationalLandingView,
    InternationalLandingSectorListView,
    InternationalLandingSectorDetailView,
)
from supplier.views import SupplierProfileDetailView
from company.views import (
    PublicProfileDetailView,
    PublicProfileListView,
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
)
from admin.proxy import AdminProxyView


cache_me = cache_page(60 * 1)


urlpatterns = [
    url(
        r"^admin/",
        AdminProxyView.as_view(),
        name="admin_proxy"
    ),
    url(
        r"^api-static/admin/",
        AdminProxyView.as_view(),
        name="admin_proxy"
    ),
    url(
        r"^$",
        DomesticLandingView.as_view(),
        name="index"
    ),
    url(
        r"^international$",
        InternationalLandingView.as_view(),
        name="international"
    ),
    url(
        r"^register$",
        EnrolmentInstructionsView.as_view(),
        name="register-instructions"
    ),
    url(
        r"^register/(?P<step>.+)$",
        EnrolmentView.as_view(url_name='register', done_step_name='finished'),
        name="register"
    ),
    url(
        r"^thanks$",
        cache_me(CachableTemplateView.as_view(template_name="thanks.html")),
        name="thanks"
    ),
    url(
        r"^sorry$",
        cache_me(CachableTemplateView.as_view(template_name="sorry.html")),
        name="problem"
    ),

    url(
        r'^supplier-profile$',
        SupplierProfileDetailView.as_view(),
        name='supplier-detail'
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
]

if settings.FEATURE_PUBLIC_PROFILES_ENABLED:
    urlpatterns += [
        url(
            r'^suppliers$',
            PublicProfileListView.as_view(),
            name='public-company-profiles-list',
        ),
        url(
            r'^suppliers/(?P<company_number>.+)$',
            PublicProfileDetailView.as_view(),
            name='public-company-profiles-detail',
        ),
    ]

if settings.FEATURE_SECTOR_LANDING_PAGES_ENABLED:
    urlpatterns += [
        url(
            r"^international/sectors$",
            InternationalLandingSectorListView.as_view(),
            name="international-sector-list"
        ),
        url(
            r"^international/sectors/(?P<slug>.+)$",
            InternationalLandingSectorDetailView.as_view(),
            name="international-sector-detail"
        ),
    ]
