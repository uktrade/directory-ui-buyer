from django.conf.urls import url
# from django.views.decorators.cache import cache_page

from ui.views import CachableTemplateView, IndexView


urlpatterns = [
    # url(r"^$", cache_page(60 * 1)(IndexView.as_view()), name="index"),
    url(r"^$", IndexView.as_view(), name="index"),

    url(r"^thanks$",
        CachableTemplateView.as_view(template_name="thanks.html"),
        name="thanks"),

    url(r"^sorry$",
        CachableTemplateView.as_view(template_name="sorry.html"),
        name="problem"),

    url(r"^terms_and_conditions$",
        CachableTemplateView.as_view(template_name="terms.html"),
        name="terms"),
]
