import pytest
from unittest import mock

from django.urls import reverse

from core.pingdom.services import RedisHealthCheck


def test_pingdom_redis_healthcheck_ok(client):
    response = client.get(reverse('pingdom'))
    assert response.status_code == 200


@mock.patch.object(RedisHealthCheck, 'check')
def test_pingdom_redis_healthcheck_false(mock_redis_check, client):
    mock_redis_check.return_value = (
        False,
        'Redis Error',
    )
    response = client.get(reverse('pingdom'))
    assert response.status_code == 500


@mock.patch.object(RedisHealthCheck, 'check')
def test_pingdom_redis_healthcheck_exception(mock_redis_check, client):
    mock_redis_check.side_effect = ConnectionRefusedError('Connection Refused')
    with pytest.raises(ConnectionRefusedError):
        response = client.get(reverse('pingdom'))
        assert response.status_code == 500
