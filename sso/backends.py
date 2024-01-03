import json
import logging

from django.conf import settings
from django.contrib import auth
from requests.exceptions import RequestException

from directory_sso_api_client import sso_api_client

logger = logging.getLogger(__name__)


class SSOUserBackend:
    MESSAGE_INVALID_JSON = (
        'SSO did not return JSON. A 502 may have occurred so SSO nginx '
        'redirected to http://sorry.great.gov.uk (see ED-2114)'
    )
    MESSAGE_NOT_SUCCESSFUL = 'SSO did not return a 200 response'

    def authenticate(self, request):
        logger.info("IN AUTHENTICATE")
        logger.info(f'SSO_SESSION_COOKIE: {settings.SSO_SESSION_COOKIE}')
        session_id = request.COOKIES.get(settings.SSO_SESSION_COOKIE)
        logger.info(f'SESSION_ID: {session_id}')
        if session_id:
            u = self.get_user(session_id)
            logger.info(f'USER: {u}')
            return u

    def get_user(self, session_id):
        try:
            response = sso_api_client.user.get_session_user(session_id)
            response.raise_for_status()
        except RequestException:
            logger.error(self.MESSAGE_NOT_SUCCESSFUL, exc_info=True)
        except json.JSONDecodeError:
            raise ValueError(self.MESSAGE_INVALID_JSON)
        else:
            return self.build_user(session_id=session_id, response=response)

    def build_user(self, session_id, response):
        parsed = response.json()
        user_kwargs = self.user_kwargs(session_id=session_id, parsed=parsed)
        SSOUser = auth.get_user_model()
        return SSOUser(**user_kwargs)

    def user_kwargs(self, session_id, parsed):
        user_profile = parsed.get('user_profile') or {}
        return {
            'id': parsed['id'],
            'pk': parsed['id'],
            'session_id': session_id,
            'hashed_uuid': parsed['hashed_uuid'],
            'email': parsed['email'],
            'has_user_profile': bool(user_profile),
            'first_name': user_profile.get('first_name'),
            'last_name': user_profile.get('last_name'),
            'job_title': user_profile.get('job_title'),
            'mobile_phone_number': user_profile.get('mobile_phone_number'),
        }
