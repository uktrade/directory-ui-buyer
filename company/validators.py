from django.forms import ValidationError

from api_client import api_client


MESSAGE_INVALID_CODE = 'Invalid code.'


def verify_with_code(sso_id):
    def inner(value):
        response = api_client.company.verify_with_code(
            sso_user_id=sso_id, code=value
        )
        if not response.ok:
            raise ValidationError(MESSAGE_INVALID_CODE)
    return inner
