from django.conf.urls import url
from django.views.decorators.cache import cache_page

from enrolment.views import (
    CachableTemplateView,
    CompanyEmailConfirmationView,
    EnrolmentView,
    FeedbackView,
    UserCompanyDescriptionEditView,
    UserCompanyProfileEditView,
    UserCompanyProfileDetailView,
    UserCompanyProfileLogoEditView,
    DomesticLandingView,
    InternationalLandingView,
    TermsView,
)
from user.views import UserProfileDetailView, UserProfileEditView

cache_me = cache_page(60 * 1)

urlpatterns = [
    url(r"^$",
        DomesticLandingView.as_view(),
        name="index"),

    url(r"^international$",
        InternationalLandingView.as_view(),
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
        cache_me(TermsView.as_view()),
        name="terms"),

    url(r'^confirm-company-email$',
        CompanyEmailConfirmationView.as_view(),
        name='confirm-company-email'),

    url(r'^company-profile$',
        UserCompanyProfileDetailView.as_view(),
        name='company-detail'),

    url(r'^user-profile$',
        UserProfileDetailView.as_view(),
        name='user-detail'),

    url(r'^user-profile/edit$',
        UserProfileEditView.as_view(),
        name='user-edit'),

    url(r'^company-profile/edit$',
        UserCompanyProfileEditView.as_view(),
        name='company-edit'),

    url(r'^company-profile/logo$',
        UserCompanyProfileLogoEditView.as_view(),
        name='company-edit-logo'),

    url(r'^company-profile/description$',
        UserCompanyDescriptionEditView.as_view(),
        name='company-edit-description'),
    url(
        r"^feedback$",
        FeedbackView.as_view(),
        name="feedback"),

]
