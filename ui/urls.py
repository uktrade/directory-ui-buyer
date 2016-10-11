from django.conf.urls import url
from django.views.decorators.cache import cache_page

from registration.views import (
    CachableTemplateView,
    EmailConfirmationView,
    RegistrationView,
    CompanyProfileEditView,
    CompanyProfileDetailView,
)


cache_me = cache_page(60 * 1)

urlpatterns = [
    url(r"^$",
        RegistrationView.as_view(),
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

    url(r'^company-profile/edit$',
        CompanyProfileEditView.as_view(),
        name='company-edit'),

]
