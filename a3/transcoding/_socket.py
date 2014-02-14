#!/usr/bin/env python
"""
Base transcoding sockets
"""


__author__ = 'RCSLabs'


from abc import ABCMeta, abstractmethod, abstractproperty


class SocketError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class ISocket(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, port, interface):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractproperty
    def port(self):
        pass

