#!/usr/bin/env python
"""
RTMP MediaPoint
"""

__author__ = 'RCSLabs'


from a3.logging import LOG
from a3.config.profile import Profile
from a3.transcoding import ITranscodingFactory, IRtmpFrontend
from a3.sdp.media_description import MediaDescription
from ._base import MediaPointError, IMediaPointListener, IMediaPoint
from a3.sdp.raw.attribute import Attribute, StrAttributeValue


class RtmpMediaPoint(IMediaPoint):
    #
    # public
    #
    def __init__(self, point_id, transcoding_factory):
        assert type(point_id) is str
        assert isinstance(transcoding_factory, ITranscodingFactory)
        super(RtmpMediaPoint, self).__init__()
        self.__point_id = point_id
        self.__listener = None
        self.__rtmp_frontend = None
        self.__local_media_description = None
        self.__transcoding_factory = transcoding_factory
        self.__profile = None
        self.__context = None

    #
    # IMediaPoint
    #
    @property
    def point_id(self):
        return self.__point_id

    def set_listener(self, listener):
        assert isinstance(listener, IMediaPointListener)
        self.__listener = listener

    def set_profile(self, profile):
        assert type(profile) is Profile
        self.__profile = profile

    def start(self):
        LOG.debug("RtmpMediaPoint %s: starting", self.__point_id)
        assert self.__profile
        #
        # Currently we accept points with local media description set before start
        #
        assert self.__local_media_description
        media_type = self.__local_media_description.media_type
        self.__rtmp_frontend = self.__transcoding_factory.create_rtmp_frontend(media_type, self.__profile)
        assert isinstance(self.__rtmp_frontend, IRtmpFrontend)

        # fill local sdp with opened ports
        LOG.debug("RtmpMediaPoint: pub: %s, sub: %s", self.__rtmp_frontend.pub, self.__rtmp_frontend.sub)

        self.__local_media_description.raw_media.attributes.append(
            Attribute("rtmp-sub", StrAttributeValue(self.__rtmp_frontend.sub)))

        self.__local_media_description.raw_media.attributes.append(
            Attribute("rtmp-pub", StrAttributeValue(self.__rtmp_frontend.pub)))

        if self.__listener is not None:
            self.__listener.media_point_frontend_ready(self)

    def stop(self):
        assert self.__rtmp_frontend
        #self.__rtmp_frontend.stop()

    def dispose(self):
        LOG.debug("RtmpMediaPoint.dispose")
        self.__rtmp_frontend.dispose()
        self.__rtmp_frontend = None

    def on_timer(self):
        pass

    def set_local_media_description(self, local_media_description):
        assert type(local_media_description) is MediaDescription
        self.__local_media_description = local_media_description

    def set_remote_media_description(self, remote_media_description):
        pass

    def set_context(self, context):
        self.__rtmp_frontend.set_context(context)

    def force_key_unit(self):
        self.__rtmp_frontend.force_key_unit()

    #
    # IMediaSourceProvider
    #
    def get_media_source(self):
        return self.__rtmp_frontend.get_media_source()

    #
    # IMediaDestinationProvider
    #
    def get_media_destination(self):
        return self.__rtmp_frontend.get_media_destination()
