# these are validators that only the UI needs. Put shared validators in
# directory-validators
import http

from directory_api_client.client import DirectoryAPIClient

from django.forms import ValidationError
from django.conf import settings


api_client = DirectoryAPIClient(
    base_url=settings.API_CLIENT_BASE_URL,
    api_key=settings.API_CLIENT_API_KEY,
)


def unique_company_number(value):
    response = api_client.company.validate_company_number(value)
    if response.status_code == http.client.BAD_REQUEST:
        raise ValidationError('Already registered. Please login.')
