from django.conf import settings


def feature_flags(request):
    return {
        'features': {
            'FEATURE_UNSUBSCRIBE_VIEW_ENABLED': (
                settings.FEATURE_UNSUBSCRIBE_VIEW_ENABLED
            ),
            'FEATURE_NEW_HEADER_FOOTER_ENABLED': (
                settings.FEATURE_NEW_HEADER_FOOTER_ENABLED
            ),
        }
    }


def analytics(request):
    return {
        'analytics': {
            'GOOGLE_TAG_MANAGER_ID': settings.GOOGLE_TAG_MANAGER_ID,
            'GOOGLE_TAG_MANAGER_ENV': settings.GOOGLE_TAG_MANAGER_ENV,
            'UTM_COOKIE_DOMAIN': settings.UTM_COOKIE_DOMAIN,
        }
    }
