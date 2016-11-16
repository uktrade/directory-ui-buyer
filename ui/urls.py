from django.conf.urls import url, include
from django.views.decorators.cache import cache_page

from enrolment.views import (
    CachableTemplateView,
    CompanyEmailConfirmationView,
    EnrolmentView,
    UserCompanyDescriptionEditView,
    UserCompanyProfileEditView,
    UserCompanyProfileDetailView,
    UserCompanyProfileLogoEditView,
    DomesticLandingView,
    InternationalLandingView,
)
from user.views import UserProfileDetailView

cache_me = cache_page(60 * 1)


urlpatterns = [
    url(r"^", include('directory_constants.urls', namespace='external')),
    url(r"^$",
        DomesticLandingView.as_view(),
        name="index"),

    url(r"^international$",
        InternationalLandingView.as_view(),
        name="international"),

    url(r"^register$",
        EnrolmentView.as_view(),
        name="register"),

    url(r"^thanks$",
        cache_me(CachableTemplateView.as_view(template_name="thanks.html")),
        name="thanks"),

    url(r"^sorry$",
        cache_me(CachableTemplateView.as_view(template_name="sorry.html")),
        name="problem"),

    url(r'^confirm-company-email$',
        CompanyEmailConfirmationView.as_view(),
        name='confirm-company-email'),

    url(r'^company-profile$',
        UserCompanyProfileDetailView.as_view(),
        name='company-detail'),

    url(r'^user-profile$',
        UserProfileDetailView.as_view(),
        name='user-detail'),

    url(r'^company-profile/edit$',
        UserCompanyProfileEditView.as_view(),
        name='company-edit'),

    url(r'^company-profile/logo$',
        UserCompanyProfileLogoEditView.as_view(),
        name='company-edit-logo'),

    url(r'^company-profile/description$',
        UserCompanyDescriptionEditView.as_view(),
        name='company-edit-description'),

]
