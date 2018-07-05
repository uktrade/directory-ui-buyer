from django.contrib import sitemaps
from django.urls import reverse


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return [
            'index'
            'register'
            'company-detail'
            'verify-company-hub'
            'verify-company-address'
            'verify-company-address-confirm'
            'add-collaborator'
            'remove-collaborator'
            'account-transfer',
        ]

    def location(self, item):
        return reverse(item)
