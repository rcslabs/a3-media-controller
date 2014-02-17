#!/usr/bin/env python
"""
RTMP MediaPoint
"""

__author__ = 'RCSLabs'


from a3.logging import LOG
from a3.config.profile import Profile
from a3.transcoding import ITranscodingFactory, IRtpFrontend
from a3.sdp.media_description import MediaDescription
from ._base import MediaPointError, IMediaPointListener, IMediaPoint


class RtpMediaPoint(IMediaPoint):
    #
    # public
    #
    def __init__(self, point_id, transcoding_factory):
        assert type(point_id) is str
        assert isinstance(transcoding_factory, ITranscodingFactory)
        self.__point_id = point_id
        self.__transcoding_factory = transcoding_factory
        self.__listener = None
        self.__profile = None

    #
    # IMediaPoint
    #
    def point_id(self):
        return self.__point_id

    def set_listener(self, listener):
        assert isinstance(listener, IMediaPointListener)
        self.__listener = listener

    def set_profile(self, profile):
        assert type(profile) is Profile
        self.__profile = profile

    def start(self):
        pass

    def stop(self):
        pass

    def dispose(self):
        pass

    def on_timer(self):
        pass

    def set_local_media_description(self, local_media_description):
        pass

    def set_remote_media_description(self, remote_media_description):
        pass

    def add_to_pipeline(self, pipeline):
        pass

    def remove_from_pipeline(self, pipeline):
        pass
