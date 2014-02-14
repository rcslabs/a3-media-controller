#!/usr/bin/env python
"""
    Default config

"""

import socket
from ._base import IConfig
from .profile import Profile
from .message_queue_url import MessageQueueUrl


try:
    machine_ip = socket.gethostbyname(socket.gethostname())
except socket.gaierror:
    machine_ip = "127.0.0.1"


class DefaultConfig(IConfig):
    def __init__(self):
        super(DefaultConfig, self).__init__()
        self.__message_queue_url = MessageQueueUrl("redis", "127.0.0.1", None, "media-controller")
        self.__default_profile = Profile(machine_ip + ":* (0.0.0.0)")
        self.__local_profile = Profile("127.0.0.1:* (127.0.0.1)")

    @property
    def mq(self):
        return self.__message_queue_url

    @property
    def profiles(self):
        return set(["", "local"])

    def profile(self, name):
        if name == "":
            return self.__default_profile
        if name == "local":
            return self.__local_profile
        return None
