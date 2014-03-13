#!/usr/bin/env python
"""
Srtp decorator for media point


"""

__author__ = 'RCSLabs'

import binascii

from a3.logging import LOG
from a3.config import IConfig, Profile
from netpoint.balancer import Balancer
from a3.sdp.direction import SdpDirection
from a3.sdp.media_description import MediaDescription
from a3.transcoding._base import ITranscodingFactory
from ._media_point_decorator import MediaPointDecorator
from .rtp_media_point import RtpMediaPoint


class SrtpMediaPoint(MediaPointDecorator):
    def __init__(self, media_point, balancer, config, transcoding_factory):
        assert type(media_point) is RtpMediaPoint
        assert type(balancer) is Balancer
        assert isinstance(config, IConfig)
        assert isinstance(transcoding_factory, ITranscodingFactory)

        self.__local_media_description = None
        self.__balancer = balancer
        self.__config = config
        self.__transcoding_factory = transcoding_factory
        self.__profile = None

        super(SrtpMediaPoint, self).__init__(media_point)

        self._media_point.set_profile(self.__config.profile("local"))

        self.__local_rtp_conn = None
        self.__local_rtcp_conn = None
        self.__remote_conn = None
        self.__agent = balancer.get_rtp_agent()
        self.__timer = 0

    #
    # IMediaPoint
    #
    def set_profile(self, profile):
        assert type(profile) is Profile
        self.__profile = profile

    def stop(self):
        super(SrtpMediaPoint, self).stop()
        self.__agent.send_message({
            "type": "REMOVE_LOCAL_STREAM",
            "pointId": self.point_id,
            "ssrc": self.__local_media_description.streams[0].ssrc_id
        })
        self.__agent.send_message({"type": "REMOVE_POINT", "id": self.point_id})
        self.__agent.close_conn(self.__remote_conn)
        self.__agent.close_conn(self.__local_rtp_conn)
        self.__agent.close_conn(self.__local_rtcp_conn)
        self.__remote_conn = None
        self.__local_rtp_conn = None
        self.__local_rtcp_conn = None

    def on_timer(self):
        self._media_point.on_timer()
        self.__timer += 1
        #if self._media_point.media_type is MediaType.VIDEO:
        if self.__timer % 10 == 0:
            self.force_key_unit()

    def set_local_media_description(self, local_media_description):
        assert type(local_media_description) is MediaDescription
        self.__local_media_description = local_media_description
        self._media_point.set_local_media_description(self.__local_media_description)

    def set_remote_media_description(self, remote_media_description):
        assert type(remote_media_description) is MediaDescription
        self._remote_media = remote_media_description
        remote_media_description.set_addr(self.__local_rtp_conn.port, "127.0.0.1")
        remote_media_description.rtcp.port = self.__local_rtcp_conn.port

        self._media_point.set_remote_media_description(remote_media_description)

        add_point_message = dict(
            type="ADD_POINT",
            id=self.point_id,
            localRtp=self.__local_rtp_conn.id,
            localRtcp=self.__local_rtcp_conn.id,
            remoteRtp=self.__remote_conn.id,
            remoteRtcp=self.__remote_conn.id,
            localIce=self.__local_media_description.ice.ufrag + ":" + self.__local_media_description.ice.pwd,
            remoteIce=self._remote_media.ice.ufrag + ":" + self._remote_media.ice.pwd)
        self.__agent.send_message(add_point_message)

        local_crypto_key = binascii.b2a_hex(binascii.a2b_base64(self.__local_media_description.crypto.key))
        self.__agent.send_message({
            "type": "ADD_LOCAL_STREAM",
            "pointId": self.point_id,
            "key": local_crypto_key,
            "ssrc": self.__local_media_description.streams[0].ssrc_id})

        remote_crypto_key = binascii.b2a_hex(binascii.a2b_base64(self._remote_media.crypto.key))
        if len(self._remote_media.streams):
            self.__agent.send_message({
                "type": "ADD_REMOTE_STREAM",
                "pointId": self.point_id,
                "key": remote_crypto_key,
                "ssrc": self._remote_media.streams[0].ssrc_id,
                "rtp": "udp://127.0.0.1:" + str(self._media_point.rtp_port),
                "rtcp": "udp://127.0.0.1:" + str(self._media_point.rtcp_port)})

        ####### draw debug scheme
        LOG.debug("""
                                +-- ice --+                   +-- gst -- +
                                !         !                   !          !
                                !        %05d <----rtp----> %05d       !
        Chrome ? <----------->%05d       !                   !          !
                                !        %05d <----rtcp---> %05d       !
                                !         !                   !          !
                                +---------+                   +----------+

        """,
                  self.__local_rtp_conn.port, self._media_point.rtp_port,
                  self.__remote_conn.port,
                  self.__local_rtcp_conn.port, self._media_point.rtcp_port)

    #
    # IMediaPointListener
    #
    def media_point_frontend_ready(self, media_point):
        LOG.debug("SrtpMediaPoint.media_point_frontend_ready")
        self.__local_media_description.direction = SdpDirection.SEND_RECV

        media_type = self.__local_media_description.media_type
        #ssrc_id = 2222L if media_type is MediaType.VIDEO else 1111L
        ssrc_id = self._media_point.transcoder.ssrc_id

        self.__local_media_description.streams.generate(ssrc_id=ssrc_id, media_type=media_type)
        #self._media_point.transcoder.ssrc_id = self.__local_media_description.streams[0].ssrc_id
        self._media_point.transcoder.cname = self.__local_media_description.streams[0].cname

        remote_profile = self.__profile
        local_profile = self.__config.profile("local")
        self.__agent.request_conn(remote_profile, lambda conn: self.__remote_conn_created(conn))
        self.__agent.request_conn(local_profile, lambda conn: self.__local_rtp_conn_created(conn))
        self.__agent.request_conn(local_profile, lambda conn: self.__local_rtcp_conn_created(conn))

    #
    # private
    #
    def force_key_unit(self):
        self._media_point.force_key_unit()

    def __remote_conn_created(self, conn):
        LOG.debug("SrtpMediaPoint.remote_conn_created %s", str(conn))
        self.__remote_conn = conn
        self.__check_conn_ready()

    def __local_rtp_conn_created(self, conn):
        LOG.debug("SrtpMediaPoint.local_rtp_conn_created %s", str(conn))
        self.__local_rtp_conn = conn
        self.__check_conn_ready()

    def __local_rtcp_conn_created(self, conn):
        LOG.debug("SrtpMediaPoint.local_rtcp_conn_created %s", str(conn))
        self.__local_rtcp_conn = conn
        self.__check_conn_ready()

    def __check_conn_ready(self):
        if self.__remote_conn and self.__local_rtp_conn and self.__local_rtcp_conn:
            LOG.info("SrtpConn.check_conn_ready: %s -> %d, %d",
                     self.__remote_conn,
                     self.__local_rtp_conn.port,
                     self.__local_rtcp_conn.port)
            self.__local_media_description.add_candidate(self.__remote_conn.port, self.__profile.ip)

            if self._listener is not None:
                self._listener.media_point_frontend_ready(self)
