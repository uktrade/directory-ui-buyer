from django.conf.urls import url
from django.views.decorators.cache import cache_page
from django.views.generic import RedirectView

from enrolment import constants
from enrolment.views import (
    CachableTemplateView,
    CompanyEmailConfirmationView,
    ContactView,
    EnrolmentView,
    FeedbackView,
    UserCompanyDescriptionEditView,
    UserCompanyProfileEditView,
    UserCompanyProfileDetailView,
    UserCompanyProfileLogoEditView,
    DomesticLandingView,
    InternationalLandingView,
    TermsView,
    NewToExportingView,
)
from user.views import UserProfileDetailView

cache_me = cache_page(60 * 1)


external_urls = [

    url(r"^terms_and_conditions$",
        RedirectView.as_view(url=constants.TERMS_AND_CONDITIONS_URL),
        name="terms"),

    url(r"^new_to_exporting$",
        RedirectView.as_view(url=constants.NEW_TO_EXPORTING_URL),
        name="new-to-exporting"),

    url(r"^feedback$",
        RedirectView.as_view(url=constants.FEEDBACK_FORM_URL),
        name="feedback"),

    url(r"^contact$",
        RedirectView.as_view(url=constants.CONTACT_US_URL),
        name="contact"),

    url(r"^events$",
        RedirectView.as_view(url=constants.EVENTS_URL),
        name="events"),

    url(r"^export_oppertunities$",
        RedirectView.as_view(url=constants.EXPORT_OPPERTUNITIES_URL),
        name="export_oppertunities"),

    url(r"^find_a_buyer$",
        RedirectView.as_view(url=constants.FIND_A_BUYER_URL),
        name="find_a_buyer"),

    url(r"^occasional_exporter$",
        RedirectView.as_view(url=constants.OCCASIONAL_EXPORTER_URL),
        name="occasional_exporter"),

    url(r"^regular_exporter$",
        RedirectView.as_view(url=constants.REGULAR_EXPORTER_URL),
        name="regular_exporter"),
    
    url(r"^selling_online_overseas$",
        RedirectView.as_view(url=constants.SELLING_ONLINE_VERSEAS_URL),
        name="selling_online_overseas"),

]

urlpatterns = external_urls + [
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
