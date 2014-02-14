#!/usr/bin/env python
"""
Base config
"""

__author__ = 'RCSLabs'


from ..logging import LOG

from abc import ABCMeta, abstractmethod, abstractproperty
import re


from .profile import Profile, ProfileError
from .message_queue_url import MessageQueueUrl, MessageQueueUrlError


class IConfig(object):
    __metaclass__ = ABCMeta

    @abstractproperty
    def mq(self):
        """return message query url"""

    @abstractmethod
    def profile(self, name):
        """return profile for name"""

    @abstractproperty
    def profiles(self):
        """return set of interfaces in use"""

    def __str__(self):
        """string representation of all values """
        result = "mq=" + str(self.mq) + "\n"
        result += "profiles:\n"
        for name in self.profiles:
            profile = self.profile(name)
            result += "  " + (name or "default") + "=" + str(profile) + "\n"
        return result


class ConfigParseError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class BaseConfig(IConfig):

    LINE_PARSER = "^\s*(?:--)?([\w\.\-\_]+)\s*=\s*(.*?)\s*(?:#.*)?$"

    def __init__(self):
        super(BaseConfig, self).__init__()
        self._mq = None
        self._profiles = {}

    @property
    def mq(self):
        return self._mq

    @property
    def profiles(self):
        return set(self._profiles.keys())

    def profile(self, name):
        return self._profiles[name] if name in self._profiles else None

    def parse_from_line(self, line):
        assert type(line) is str
        g = re.match(self.LINE_PARSER, line)
        if not g:
            raise ConfigParseError("Could not parse %s" % (line,))
        name = g.group(1)
        value = g.group(2)
        if name == "mq":
            self.__parse_media_queue_url_value(name, value)
        elif re.match("^profile(?:-(.*))?$", name):
            self.__parse_profile_value(name, value)
        else:
            raise ConfigParseError("Could not parse %s" % (line,))

    def __parse_media_queue_url_value(self, name, value):
        assert name == "mq"
        assert type(value) is str
        try:
            self._mq = MessageQueueUrl.from_string(value)
        except MessageQueueUrlError as e:
            raise ConfigParseError("Could not parse media queue %s (%s)" % (value, str(e)))

    def __parse_profile_value(self, name, value):
        assert type(name) is str
        assert type(value) is str
        g = re.match("^profile(?:-(.*))?$", name)
        assert g is not None
        profile_name = g.group(1) if g.group(1) is not None and g.group(1) != "default" else ""
        try:
            self._profiles[profile_name] = Profile(value)
        except ProfileError as e:
            raise ConfigParseError("Could not parse profile %s (%s)" % (value, str(e)))


class ChainedConfig(BaseConfig):
    """
    implements Config chain of responsibility
    """
    def __init__(self, next_):
        assert isinstance(next_, IConfig)
        super(ChainedConfig, self).__init__()
        self._next = next_

    @property
    def mq(self):
        return super(ChainedConfig, self).mq or self._next.mq

    @property
    def profiles(self):
        return super(ChainedConfig, self).profiles | self._next.profiles

    def profile(self, name):
        return super(ChainedConfig, self).profile(name) or self._next.profile(name)

