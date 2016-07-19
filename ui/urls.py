from django.conf.urls import url
from django.views.generic import TemplateView

from ui.views import IndexView


from django.views.decorators.cache import cache_page
urlpatterns = [
    url(r"^$", cache_page(60 * 1)(IndexView.as_view()), name="index"),

    url(r"^thanks$",
        TemplateView.as_view(template_name="thanks.html"),
        name="thanks"),

    url(r"^sorry$",
        TemplateView.as_view(template_name="sorry.html"),
        name="problem"),

    url(r"^terms_and_conditions$",
        TemplateView.as_view(template_name="terms.html"),
        name="terms"),
]
