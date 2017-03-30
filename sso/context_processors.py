from django.conf import settings


def sso_user_processor(request):
    url = request.build_absolute_uri()
    return {
        'sso_is_logged_in': request.sso_user is not None,
        'sso_login_url': '{0}?next={1}'.format(settings.SSO_LOGIN_URL, url),
        'sso_register_url': settings.SSO_SIGNUP_URL,
        'sso_logout_url': settings.SSO_LOGOUT_URL,
        'sso_profile_url': settings.SSO_PROFILE_URL,
    }
