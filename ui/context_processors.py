from django.conf import settings


def feature_flags(request):
    return {
        'features': {
            'FEATURE_COMPANIES_HOUSE_OAUTH2_ENABLED': (
                settings.FEATURE_COMPANIES_HOUSE_OAUTH2_ENABLED
            ),
        }
    }
