from django.conf import settings


def feature_flags(request):
    return {
        'FEATURE_PUBLIC_PROFILES': settings.FEATURE_PUBLIC_PROFILES,
    }
