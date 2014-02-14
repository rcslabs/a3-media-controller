#!/usr/bin/env python
"""

"""


from abc import ABCMeta, abstractmethod, abstractproperty


class IMessage(object):
    __metaclass__ = ABCMeta

    @abstractproperty
    def type(self):
        """
        return message type
        """

    @abstractmethod
    def get(self, key, default_value=None):
        """
        get value for key
        """

    @abstractmethod
    def set(self, key, value):
        """
        set value for key
        """

    @abstractmethod
    def all(self):
        """
        return iterable pairs of (key, value)
        """


class ParseException(Exception):
    def __init__(self, value):
        self.__value = value

    def __str__(self):
        return repr(self.__value)


class ISerDes(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def serialize(self, message):
        """
        serialize message to string
        """

    @abstractmethod
    def deserialize(self, string):
        """
        create a message from string
        """
