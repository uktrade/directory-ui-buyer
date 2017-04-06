from sigauth.utils import RequestSigner, RequestSignatureChecker

from django.conf import settings


api_signer = RequestSigner(settings.API_CLIENT_KEY)
external_api_checker = RequestSignatureChecker(
    settings.DIRECTORY_EXTERNAL_API_CLIENT_KEY
)
