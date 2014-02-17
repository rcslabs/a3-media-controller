#!/usr/bin/env python
"""

"""

from abc import abstractmethod, ABCMeta

from a3.logging import LOG
from a3.sdp.session_description import SessionDescription
from a3.transcoding._base import ITranscodingFactory
from a3.config import IConfig
from a3.config.profile import Profile
from ._base import MediaPointError, IMediaPointListener
from .rtp_media_point import RtpMediaPoint
from .srtp_media_point import SrtpMediaPoint
from ._dtmf_media_point import DtmfMediaPoint
from ._filesave_media_point import FilesaveMediaPoint


class IPointListener(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def point_conn_ready(self):
        """
        Is called when point opens its ports
        """


#class PointError(Exception):
#    def __init__(self, value):
#        self.value = value
#
#    def __str__(self):
#        return str(self.value)


class Point(IMediaPointListener):
    def __init__(self, point_id, listener, local_sdp, balancer, config, transcoding_factory, profile):
        assert type(point_id) is str
        assert isinstance(listener, IPointListener)
        assert type(local_sdp) is SessionDescription
        assert isinstance(config, IConfig)
        assert isinstance(transcoding_factory, ITranscodingFactory)
        assert type(profile) is Profile

        self.__point_id = point_id
        self.__listener = listener
        self.__local_sdp = local_sdp
        self.__config = config
        self.__transcoding_factory = transcoding_factory
        self.__profile = profile

        self.__dtmf_sender = None

        self.__remote_sdp = None
        self.__audio_point = None
        self.__video_point = None
        self.__audio_point_ready = not bool(self.__local_sdp.audio)
        self.__video_point_ready = not bool(self.__local_sdp.video)
        if self.__local_sdp.audio:
            self.__audio_point = RtpMediaPoint(self.__point_id + ".audio", self.__transcoding_factory)

            if self.__local_sdp.audio.crypto:
                self.__audio_point = SrtpMediaPoint(self.__audio_point,
                                                    balancer=balancer,
                                                    config=config,
                                                    transcoding_factory=self.__transcoding_factory)

            # add saving capability
            #self.__add_filesave_capability()

            # add dtmf
            self.__add_dtmf_capability()

            self.__audio_point.set_listener(self)
            self.__audio_point.set_profile(self.__profile)
            self.__audio_point.set_local_media_description(self.__local_sdp.audio)

        if self.__local_sdp.video:
            self.__video_point = RtpMediaPoint(self.__point_id + ".video", self.__transcoding_factory)

            if self.__local_sdp.video.crypto:
                self.__video_point = SrtpMediaPoint(self.__video_point,
                                                    balancer=balancer,
                                                    config=config,
                                                    transcoding_factory=self.__transcoding_factory)

            self.__video_point.set_listener(self)
            self.__video_point.set_profile(self.__profile)
            self.__video_point.set_local_media_description(self.__local_sdp.video)

        LOG.debug("Point.init [%s], audio=%s, video=%s", self.__point_id, self.__audio_point, self.__video_point)

    #
    # Public:
    #
    @property
    def audio_point(self):
        return self.__audio_point

    @property
    def video_point(self):
        return self.__video_point

    def start(self):
        LOG.debug("Point.start [%s]", self.__point_id)
        if self.__audio_point:
            self.__audio_point.start()
        if self.__video_point:
            self.__video_point.start()

    def stop(self):
        LOG.debug("Point.stop [%s]", self.__point_id)
        if self.__audio_point:
            self.__audio_point.stop()
        if self.__video_point:
            self.__video_point.stop()

    def dispose(self):
        LOG.debug("Point.dispose [%s]", self.__point_id)
        if self.__audio_point:
            self.__audio_point.dispose()
        if self.__video_point:
            self.__video_point.dispose()
        self.__local_sdp = None
        self.__remote_sdp = None
        self.__audio_point = None
        self.__video_point = None
        self.__audio_point_ready = False
        self.__video_point_ready = False

    def on_timer(self):
        if self.__audio_point:
            self.__audio_point.on_timer()
        if self.__video_point:
            self.__video_point.on_timer()

    @property
    def local_sdp(self):
        return self.__local_sdp

    @property
    def remote_sdp(self):
        return None

    @remote_sdp.setter
    def remote_sdp(self, remote_sdp):
        assert type(remote_sdp) is SessionDescription
        if self.__remote_sdp:
            self.__update_remote_sdp(remote_sdp)
        else:
            self.__set_remote_sdp(remote_sdp)

    def media_point_frontend_ready(self, media_point):
        if media_point is self.__audio_point:
            self.__audio_point_ready = True
        elif media_point is self.__video_point:
            self.__video_point_ready = True
        else:
            # Unknown media point
            assert 0

        LOG.debug("Point.media_point_frontend_ready [%s, %s]", self.__audio_point_ready, self.__video_point_ready)
        if self.__audio_point_ready and self.__video_point_ready:
            #
            # HACK!
            # Fix c= parameter for backward compatibility
            # - only for SIP calls
            #
            #
            if self.__local_sdp.audio and self.__local_sdp.audio.crypto or \
               self.__local_sdp.video and self.__local_sdp.video.crypto:
                pass
            else:
                host = self.__profile.ip

                self.__local_sdp.host = host
                self.__local_sdp.origin_value.unicast_address = host

                if self.__local_sdp.audio:
                    self.__local_sdp.audio.connection_data = None
                if self.__local_sdp.video:
                    self.__local_sdp.video.connection_data = None

            if self.__listener:
                self.__listener.point_conn_ready()

    def send_dtmf(self, dtmf):
        if self.__dtmf_sender:
            self.__dtmf_sender.send_dtmf(dtmf)
        else:
            LOG.warning("Point: send dtmf: no dtmf_sender available on the point %s", self.__point_id)

    #
    # Private
    #
    def __update_remote_sdp(self, remote_sdp):
        """
        TODO: not implemented
        """
        LOG.warning("Trying to update remote SDP for point: NOT IMPLEMENTED")

    def __set_remote_sdp(self, remote_sdp):
        assert type(remote_sdp) is SessionDescription
        LOG.debug("Point.remote_sdp [%s]\n%s", self.__point_id, remote_sdp)
        self.__remote_sdp = remote_sdp
        try:
            if self.__local_sdp.audio and self.__remote_sdp.audio:
                assert self.__audio_point
                self.__audio_point.set_remote_media_description(self.__remote_sdp.audio)
        except MediaPointError as e:
            LOG.warning("Point:: set remote media: failed to create audio point")
            self.__audio_point.stop()
            self.__audio_point = None
            self.__audio_point_ready = True

        try:
            if self.__local_sdp.video and self.__remote_sdp.video:
                assert self.__video_point
                self.__video_point.set_remote_media_description(self.__remote_sdp.video)
        except MediaPointError, e:
            LOG.warning("Point:: set remote media: failed to create video point")
            self.__video_point.stop()
            self.__video_point = None
            self.__video_point_ready = True

    def __add_filesave_capability(self):
        self.__audio_point = FilesaveMediaPoint(self.__audio_point, self.__transcoding_factory)

    def __add_dtmf_capability(self):
        self.__audio_point = DtmfMediaPoint(self.__audio_point, self.__transcoding_factory)
        self.__dtmf_sender = self.__audio_point
