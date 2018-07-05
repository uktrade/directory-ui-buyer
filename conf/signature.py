from sigauth.utils import RequestSigner, RequestSignatureChecker

from django.conf import settings


api_signer = RequestSigner(settings.API_SIGNATURE_SECRET)
external_api_checker = RequestSignatureChecker(
    settings.DIRECTORY_EXTERNAL_API_SIGNATURE_SECRET
)
