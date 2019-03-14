import pytest


@pytest.fixture(autouse=True)
def feature_flags(settings):
    # solves this issue: https://github.com/pytest-dev/pytest-django/issues/601
    settings.FEATURE_FLAGS = {**settings.FEATURE_FLAGS}
    yield settings.FEATURE_FLAGS
