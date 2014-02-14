#!/usr/bin/env python
"""
RTP MediaPoint
"""

__author__ = 'RCSLabs'


from a3.sdp.media_description import MediaDescription

from a3.logging import LOG
from a3.config.profile import Profile
from a3.transcoding import ITranscodingFactory, IRtpFrontend

from ._base import MediaPointError, IMediaPointListener, IMediaPoint


class RtpMediaPoint(IMediaPoint):
    def __init__(self, point_id, transcoding_factory):
        assert type(point_id) is str
        assert isinstance(transcoding_factory, ITranscodingFactory)
        super(RtpMediaPoint, self).__init__()
        self.__point_id = point_id
        self.__listener = None
        self.__rtp_frontend = None
        self.__local_media_description = None
        self.__transcoding_factory = transcoding_factory
        self.__profile = None
        #self.__fake_room = None

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

    @property
    def rtp_port(self):
        assert self.__rtp_frontend
        return self.__rtp_frontend.rtp_port

    @property
    def rtcp_port(self):
        assert self.__rtp_frontend
        return self.__rtp_frontend.rtcp_port

    def start(self):
        LOG.debug("MediaPoint %s: starting", self.__point_id)
        assert self.__profile
        #
        # Currently we accept points with local media description set before start
        #
        assert self.__local_media_description
        media_type = self.__local_media_description.media_type
        self.__rtp_frontend = self.__transcoding_factory.create_rtp_frontend(media_type, self.__profile)
        assert isinstance(self.__rtp_frontend, IRtpFrontend)

        # fill local sdp with opened ports
        LOG.debug("MediaPoint: opened ports: %i, %i", self.__rtp_frontend.rtp_port, self.__rtp_frontend.rtcp_port)
        self.__local_media_description.set_addr(self.__rtp_frontend.rtp_port, self.__profile.ip)
        if self.__listener is not None:
            self.__listener.media_point_frontend_ready(self)

    def stop(self):
        assert self.__rtp_frontend
        self.__rtp_frontend.stop()

    def dispose(self):
        LOG.debug("RtpMediaPoint.dispose")
        self.__rtp_frontend.dispose()
        self.__rtp_frontend = None

    def set_remote_media_description(self, remote_media_description):
        """
        raises: MediaPointError
        """
        assert type(remote_media_description) is MediaDescription
        self.__remote_media_description = remote_media_description
        LOG.debug("MediaPoint: Got remote sdp: %s:%d",
                  self.__remote_media_description.host,
                  self.__remote_media_description.rtp_port)

        if remote_media_description.rtp_port == 0:
            raise MediaPointError(MediaPointError.MEDIA_DECLINED)

        local_rtp_codecs = self.__local_media_description.rtp_codecs
        remote_rtp_codecs = self.__remote_media_description.rtp_codecs

        local_codecs = [rtp_codec.codec for rtp_codec in local_rtp_codecs]
        remote_codecs = [rtp_codec.codec for rtp_codec in remote_rtp_codecs]

        common_codecs = list(set(local_codecs) & set(remote_codecs))
        if len(common_codecs) == 0:
            LOG.warning("MediaPoint: No common codecs: local={%s}, remote={%s}",
                        ", ".join([str(c) for c in local_codecs]),
                        ", ".join([str(c) for c in remote_codecs]))
            raise MediaPointError(MediaPointError.CODEC_INCONSISTENCY)

        LOG.info("MediaPoint: Common codecs: %s", ",".join([str(c) for c in common_codecs]))

        local_rtp_codecs = [c for c in local_rtp_codecs if c in common_codecs]
        remote_rtp_codecs = [c for c in remote_rtp_codecs if c in common_codecs]

        LOG.info("Local codecs with payload types: %s", ",".join([str(c) for c in local_rtp_codecs]))
        LOG.info("Remote codecs with payload types: %s", ",".join([str(c) for c in remote_rtp_codecs]))

        self.__rtp_frontend.create_sender(local_rtp_codecs,
                                          self.__remote_media_description.host,
                                          self.__remote_media_description.rtp_port,
                                          self.__remote_media_description.rtcp_port)

        self.__rtp_frontend.create_receiver(remote_rtp_codecs)

        #self.__fake_room = FakeRoom()
        #self.__fake_room.add_transcoder(self.__transcoder)
        #self.__fake_room.play()

    def set_local_media_description(self, local_media_description):
        assert type(local_media_description) is MediaDescription
        self.__local_media_description = local_media_description

    def on_timer(self):
        pass

    def add_to_pipeline(self, pipeline):
        pipeline.add(self.__rtp_frontend.gst_element)

    def remove_from_pipeline(self, pipeline):
        pipeline.remove(self.__rtp_frontend.gst_element)

    #
    # IMediaSourceProvider
    #
    def get_media_source(self):
        return self.__rtp_frontend.get_media_source()

    #
    # IMediaDestinationProvider
    #
    def get_media_destination(self):
        return self.__rtp_frontend.get_media_destination()

    #
    # private
    #
    def force_key_unit(self):
        if self.__rtp_frontend:
            self.__rtp_frontend.force_key_unit()

    @property
    def transcoder(self):
        return self.__rtp_frontend


if __name__ == "__main__":
    pass
