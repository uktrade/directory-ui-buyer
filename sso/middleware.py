from django.conf import settings

from sso.utils import SSOUser, sso_api_client


class SSOUserMiddleware:

    def process_request(self, request):
        sso_response = sso_api_client.get_session_user(
            session_id=request.COOKIES.get(settings.SSO_SESSION_COOKIE)
        )

        if sso_response.ok:
            sso_user_data = sso_response.json()

            request.sso_user = SSOUser(
                id=sso_user_data['id'],
                email=sso_user_data['email']
            )

        else:
            request.sso_user = None
