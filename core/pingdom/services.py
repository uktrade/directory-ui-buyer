import redis
from redis.exceptions import ConnectionError
from urllib.parse import urlparse

from django.conf import settings

class RedisHealthCheck:
    name = 'redis'

    def check(self):
        o = urlparse(settings.REDIS_URL)
        rs = redis.Redis(host=o.hostname,port=o.port,db=0)
        try:
            rs.ping()
        except (ConnectionError, ConnectionRefusedError) as e:
            return False, e
        else:
            return True, ''

health_check_services = (RedisHealthCheck,)