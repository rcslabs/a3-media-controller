#!/usr/bin/env python
"""
Redis message transport
"""


from _base import MessagingTransport
import logging
import time


LOGGER = logging.getLogger("MC")


class RedisTransport(MessagingTransport):
    def __init__(self, host, port, channel_name):
        import redis
        self.__redis = redis

        assert type(host) is str
        assert port is None or type(port) is int
        assert type(channel_name) is str
        MessagingTransport.__init__(self)
        self.__host = host
        self.__port = port
        self.__channel_name = channel_name

    def __connect(self):
        if self.__port is None:
            self.__connection = self.__redis.StrictRedis(host=self.__host, db=0)
        else:
            self.__connection = self.__redis.StrictRedis(host=self.__host, port=self.__port, db=0)
        self.__sub = self.__connection.pubsub()
        self.__sub.subscribe(self.__channel_name)
        LOGGER.debug("Redis: connected")

    def send_message(self, message, channel=None):
        assert type(channel) is str
        self.__connection.publish(channel, message)

    def listen(self):
        interval = 1
        while True:
            try:
                LOGGER.debug("Redis: connecting...")
                self.__connect()
                interval = 1
                for m in self.__sub.listen():
                    if m["type"] == "message":
                        self.message_received(m["data"])
            except self.__redis.exceptions.ConnectionError:
                LOGGER.warning("Redis: connection error. Trying to reconnect in %d sec...", interval)
                time.sleep(interval)
                interval *= 2
                if interval > 16:
                    interval = 16

    @property
    def channel_name(self):
        return self.__channel_name
