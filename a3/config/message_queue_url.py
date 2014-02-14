#!/usr/bin/env python
"""
MessageQueueUrl
"""


import re


class MessageQueueUrlError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class MessageQueueUrl(object):
    def __init__(self, protocol, server, port, channel):
        assert type(protocol) is str
        assert type(server) is str
        assert port is None or type(port) is int
        assert type(channel) is str

        self.__protocol = protocol
        self.__server = server
        self.__port = port
        self.__channel = channel

    @property
    def protocol(self):
        return self.__protocol

    @protocol.setter
    def protocol(self, protocol):
        assert type(protocol) is str
        self.__protocol = protocol

    @property
    def server(self):
        return self.__server

    @server.setter
    def server(self, server):
        assert type(server) is str
        self.__server = server

    @property
    def port(self):
        return self.__port

    @port.setter
    def port(self, port):
        assert port is None or type(port) is int
        self.__port = port

    @property
    def channel(self):
        return self.__channel

    @channel.setter
    def channel(self, channel):
        assert type(channel) is str
        self.__channel = channel

    def __str__(self):
        if self.port is not None:
            return "%s://%s:%d/%s" % (self.protocol, self.server, self.port, self.channel)
        else:
            return "%s://%s/%s" % (self.protocol, self.server, self.channel)

    @classmethod
    def from_string(cls, url_str):
        assert type(url_str) is str
        g = re.match("(.+?)://(.+?)(?::(\d+))?(?:/(.+))?$", url_str)
        if g is None:
            raise MessageQueueUrlError("Could not parse %s" % (url_str,))
        return cls(protocol=g.group(1),
                   server=g.group(2),
                   port=int(g.group(3)) if g.group(3) is not None else None,
                   channel=g.group(4))
