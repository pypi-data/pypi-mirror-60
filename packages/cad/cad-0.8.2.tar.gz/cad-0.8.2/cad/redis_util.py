#!/usr/bin/env python
# -*- coding:utf-8 _*-  
"""
@author  : Bruce Liu
@time    : 2020/1/3 11:01
@contact : bruce.liu@wayz.ai
"""

from redis import ConnectionPool, Redis


class RedisUtil(object):
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0, password: str = '', url_str: str = None,
                 **kwargs):
        if url_str is not None:
            hosts = url_str.split(':')
            host = hosts[0]
            ports = hosts[1].split('/')
            port = ports[0]
            db = ports[1]
        self._pool = ConnectionPool(host=host, port=port, db=db, password=password, **kwargs)
        self._redis = Redis(connection_pool=self._pool)

    @property
    def redis(self):
        return self._redis

    @property
    def pool(self):
        return self._pool
