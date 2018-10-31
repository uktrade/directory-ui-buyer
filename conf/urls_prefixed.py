from django.conf.urls import url, include

import conf.urls


urlpatterns = [
    url(
        r'^find-a-buyer/',
        include(conf.urls.urlpatterns)
    )
]
