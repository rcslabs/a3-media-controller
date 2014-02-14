#!/usr/bin/env python


from abc import abstractmethod, ABCMeta


class AttributeValue(object):
    __metaclass__ = ABCMeta

    @classmethod
    @abstractmethod
    def from_string(cls, str_value):
        """
        Parse an attribute value from string and return a new instance of attribute value class
        :param str_value: a part of sdp line which represents an attribute value
        """

    @abstractmethod
    def __str__(self):
        """
        Return string representation of value to insert to SDP
        """


class FlagAttributeValue(AttributeValue):
    """
    An attribute value which is always empty
    """
    def __init__(self):
        pass

    def __str__(self):
        assert not "Flag does not have a value"

    @classmethod
    def from_string(cls, string):
        assert string is None
        return cls()


class StrAttributeValue(AttributeValue):
    """
    Any attribute which has string as a value
    """
    def __init__(self, value):
        assert type(value) is str
        self.__value = value

    def __str__(self):
        return self.__value

    @classmethod
    def from_string(cls, string):
        return cls(string)

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

