import pytest

from sso.utils import SSOUser


@pytest.fixture(autouse=True)
def feature_flags(settings):
    # solves this issue: https://github.com/pytest-dev/pytest-django/issues/601
    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS}
    yield settings.FEATURE_FLAGS


@pytest.fixture
def sso_user():
    return SSOUser(
        id=1,
        email='jim@example.com',
        session_id='213'
    )
