from django.conf import settings
from django.utils.module_loading import import_string


ClientClass = import_string(settings.API_CLIENT_CLASS)
api_client = ClientClass(
    base_url=settings.API_CLIENT_BASE_URL,
    api_key=settings.API_SIGNATURE_SECRET,
)
