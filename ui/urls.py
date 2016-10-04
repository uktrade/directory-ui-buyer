from django.conf.urls import url
from django.views.decorators.cache import cache_page

from ui.views import (
    CachableTemplateView,
    RegisterView,
    IndexView,
)


cache_me = cache_page(60 * 1)

urlpatterns = [
    url(r"^$", cache_me(IndexView.as_view()), name="index"),

    url(r"^thanks$",
        cache_me(CachableTemplateView.as_view(template_name="thanks.html")),
        name="thanks"),

    url(r"^sorry$",
        cache_me(CachableTemplateView.as_view(template_name="sorry.html")),
        name="problem"),

    url(r"^terms_and_conditions$",
        cache_me(CachableTemplateView.as_view(template_name="terms.html")),
        name="terms"),

    url(r'^register$',
        RegisterView.as_view(),
        name='register'),

]
