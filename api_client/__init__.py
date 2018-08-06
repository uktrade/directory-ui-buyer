from django.conf import settings
from django.utils.module_loading import import_string


ClientClass = import_string(settings.API_CLIENT_CLASS)
api_client = ClientClass(
    base_url=settings.DIRECTORY_API_CLIENT_BASE_URL,
    api_key=settings.DIRECTORY_API_CLIENT_API_KEY,
    sender_id=settings.DIRECTORY_API_CLIENT_SENDER_ID,
    timeout=settings.DIRECTORY_API_CLIENT_DEFAULT_TIMEOUT,
)
