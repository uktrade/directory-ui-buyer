from sigauth.helpers import RequestSigner, RequestSignatureChecker

from django.conf import settings


api_signer = RequestSigner(
    secret=settings.DIRECTORY_API_CLIENT_API_KEY,
    sender_id='directory'
)
external_api_checker = RequestSignatureChecker(
    secret=settings.DIRECTORY_EXTERNAL_API_SIGNATURE_SECRET
)
