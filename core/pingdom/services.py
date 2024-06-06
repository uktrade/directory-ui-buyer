from urllib.parse import urlparse

from redis import Redis
from django.conf import settings
from redis.exceptions import ConnectionError


class RedisHealthCheck:
    name = 'redis'

    def check(self):
        o = urlparse(settings.REDIS_URL)
        rs = Redis(host=o.hostname, port=o.port, db=0)
        try:
            rs.ping()
        except (ConnectionError, ConnectionRefusedError) as e:
            return False, e
        else:
            return True, ''


health_check_services = (RedisHealthCheck,)
