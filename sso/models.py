from directory_api_client import api_client
import directory_sso_api_client.models

from django.db import models
from django.utils.functional import cached_property


class SSOUser(directory_sso_api_client.models.SSOUser):
    has_user_profile = models.BooleanField()

    @cached_property
    def company(self):
        response = api_client.company.retrieve_private_profile(self.session_id)
        if response.status_code == 404:
            return {}
        response.raise_for_status()
        parsed = response.json()

        if parsed.get('sectors'):
            parsed['sectors'] = parsed['sectors'][0]
        return parsed

    @cached_property
    def supplier(self):
        response = api_client.supplier.retrieve_profile(self.session_id)
        if response.status_code == 404:
            return {}
        response.raise_for_status()
        return response.json()
