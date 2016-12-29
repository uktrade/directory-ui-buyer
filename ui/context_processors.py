from django.conf import settings


def feature_flags(request):
    return {
        'features': {
            'FEATURE_PUBLIC_PROFILES_ENABLED': (
                settings.FEATURE_PUBLIC_PROFILES_ENABLED
            ),
        }
    }
