from django.conf.urls import url
from django.views.decorators.cache import cache_page

from enrolment.views import (
    CachableTemplateView,
    EmailConfirmationView,
    EnrolmentView,
    CompanyDescriptionEditView,
    CompanyProfileEditView,
    CompanyProfileDetailView,
    CompanyProfileLogoEditView,
    LandingView,
)
from user.views import UserProfileDetailView, UserProfileEditView

cache_me = cache_page(60 * 1)

urlpatterns = [
    url(r"^$",
        LandingView.as_view(),
        name="index"),

    url(r"^register$",
        EnrolmentView.as_view(),
        name="register"),

    url(r"^thanks$",
        cache_me(CachableTemplateView.as_view(template_name="thanks.html")),
        name="thanks"),

    url(r"^sorry$",
        cache_me(CachableTemplateView.as_view(template_name="sorry.html")),
        name="problem"),

    url(r"^terms_and_conditions$",
        cache_me(CachableTemplateView.as_view(template_name="terms.html")),
        name="terms"),

    url(r'^confirm-email$',
        EmailConfirmationView.as_view(),
        name='confirm-email'),

    url(r'^company-profile$',
        CompanyProfileDetailView.as_view(),
        name='company-detail'),

    url(r'^user-profile$',
        UserProfileDetailView.as_view(),
        name='user-detail'),

    url(r'^user-profile/edit$',
        UserProfileEditView.as_view(),
        name='user-edit'),

    url(r'^company-profile/edit$',
        CompanyProfileEditView.as_view(),
        name='company-edit'),

    url(r'^company-profile/logo$',
        CompanyProfileLogoEditView.as_view(),
        name='company-edit-logo'),

    url(r'^company-profile/description$',
        CompanyDescriptionEditView.as_view(),
        name='company-edit-description'),

]
