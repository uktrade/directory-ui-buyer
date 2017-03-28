from signature.utils import SignatureRejection


def test_has_permission_nonschema_invalid_signature(rf):
    request = rf.get('/')
    assert SignatureRejection.test_signature(request) is False


def test_has_permission_nonschema_valid_signature(rf, settings):
    signature = SignatureRejection.generate_signature(
        settings.EXTERNAL_SECRET, '/', b'',
    )
    request = rf.get('/', HTTP_X_SIGNATURE=signature)
    assert SignatureRejection.test_signature(request) is True
