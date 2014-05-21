#!/usr/bin/env python
"""
    a3.point._base
"""

__author__ = 'RCSLabs'


from abc import abstractmethod, abstractproperty, ABCMeta
from a3.transcoding import IMediaSourceProvider, IMediaDestinationProvider


class MediaPointError(Exception):
    NO_FREE_PORTS = "no free ports"
    MEDIA_DECLINED = "remote media declined"
    CODEC_INCONSISTENCY = "media inconsistency"

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class IMediaPointListener(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def media_point_frontend_ready(self, media_point):
        """
        Is called when media point opens its ports
        """

#
# Todo: concrete IMediaPoint implementations
# should implement IMediaSourceProvider, IMediaDestinationProvider
#


class IMediaPoint(IMediaSourceProvider, IMediaDestinationProvider):
    __metaclass__ = ABCMeta

    @abstractproperty
    def point_id(self):
        """
        return point id
        """

    @abstractmethod
    def set_listener(self, listener):
        """
        listener setter
        """

    @abstractmethod
    def set_profile(self, profile):
        """
        profile setter
        """

    @abstractmethod
    def start(self):
        """
        start media point
        """

    @abstractmethod
    def stop(self):
        """
        Stop media point
        """

    @abstractmethod
    def dispose(self):
        """
        completly remove media point and free its resources
        """

    @abstractmethod
    def on_timer(self):
        """
        1-second timer
        """

    @abstractmethod
    def set_local_media_description(self, local_media_description):
        """
        set remote sdp media object
        """

    @abstractmethod
    def set_remote_media_description(self, remote_media_description):
        """
        set remote sdp media object
        """

    @abstractmethod
    def set_context(self, context):
        pass
