from django.conf import settings


def feature_flags(request):
    return {
        'features': {
            'FEATURE_COMPANIES_HOUSE_OAUTH2_ENABLED': (
                settings.FEATURE_COMPANIES_HOUSE_OAUTH2_ENABLED
            ),
            'FEATURE_NEW_SHARED_HEADER_ENABLED': (
                settings.FEATURE_NEW_SHARED_HEADER_ENABLED
            )
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
