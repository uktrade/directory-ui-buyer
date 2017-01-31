from django.conf import settings


def feature_flags(request):
    return {
        'features': {
            'FEATURE_PUBLIC_PROFILES_ENABLED': (
                settings.FEATURE_PUBLIC_PROFILES_ENABLED
            ),
        }
    }


def analytics(request):
    return {
        'analytics': {
            'GOOGLE_TAG_MANAGER_ID': settings.GOOGLE_TAG_MANAGER_ID,
            'GOOGLE_TAG_MANAGER_ENV': settings.GOOGLE_TAG_MANAGER_ENV,
        }
    }
