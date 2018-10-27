from django.conf.urls import url, include

import conf.urls


urlpatterns = [
    url(
        r'^buyer/',
        include(conf.urls.urlpatterns)
    )
]
