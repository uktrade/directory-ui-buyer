import pytest
from django.urls import resolve


@pytest.mark.parametrize(
    'path,view_name',
    [
        ('/confirm-company-address/', 'verify-company-address-historic-url'),
    ]
)
def test_urls_resolve(path, view_name):
    assert resolve(path).view_name == view_name
