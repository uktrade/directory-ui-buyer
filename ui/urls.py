from django.conf.urls import url
from django.views.generic import TemplateView

from ui.views import IndexView

urlpatterns = [
    url(r"^$", IndexView.as_view(), name="index"),

    url(r"^thanks$",
        TemplateView.as_view(template_name="thanks.html"),
        name="thanks"),

    url(r"^sorry$",
        TemplateView.as_view(template_name="sorry.html"),
        name="problem"),
]
