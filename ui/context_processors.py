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
