from hashlib import sha256

from django.conf import settings
from django.utils.crypto import constant_time_compare


class SignatureRejection:

    @classmethod
    def generate_signature(self, secret, path, body):
        salt = bytes(secret, "utf-8")
        path = bytes(path, "utf-8")
        return sha256(path + body + salt).hexdigest()

    @classmethod
    def test_signature(self, request):
        offered = request.META.get("HTTP_X_SIGNATURE")

        if not offered:
            return False

        generated = self.generate_signature(
            settings.DIRECTORY_EXTERNAL_API_CLIENT_KEY,
            request.get_full_path(),
            request.body,
        )
        return constant_time_compare(generated, offered)
