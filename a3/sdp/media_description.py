#!/usr/bin/env python

#from a3.media.payload_type_reserver import PayloadTypeReserver
import raw.media
import raw.entity
import error
import ice
import crypto
import sdp_codec
import direction
import stream
import rtcp
import ptime
import silence_supp
import session_description
import mid
import raw.attribute

SdpDirection = direction.SdpDirection
SemanticError = error.SemanticError
NetType = raw.entity.NetType
AddrType = raw.entity.AddrType


class MediaDescription(object):
    def __init__(self, raw_media, parent_sdp=None):
        assert type(raw_media) is str or type(raw_media) is raw.media.Media
        assert parent_sdp is None or type(parent_sdp) is session_description.SessionDescription
        if type(raw_media) == str:
            self.__raw_media = raw.media.Media(raw_media)
        else:
            self.__raw_media = raw_media

        self.__parent_sdp = parent_sdp
        #self.__pt_reserver = self.__parent_sdp.pt_reserver if self.__parent_sdp else PayloadTypeReserver()

        self.__ice = ice.Ice(self.__raw_media.attributes)
        self.__direction = direction.Direction(self.__raw_media.attributes)
        self.__sdp_codec_collection = sdp_codec.SdpCodecCollection(self.__raw_media)
        self.__mid = mid.Mid(self.__raw_media.attributes)
        self.__crypto = crypto.Crypto(self.__raw_media.attributes)
        self.__streams = stream.StreamCollection(self.__raw_media.attributes)
        self.__rtcp_mux = rtcp.RtcpMux(self.__raw_media.attributes)
        self.__rtcp = rtcp.Rtcp(self.__raw_media.attributes)
        self.__ptime = ptime.Ptime(self.__raw_media.attributes)
        self.__silence_supp = silence_supp.SilenceSupp(self.__raw_media.attributes)

    @property
    def media_type(self):
        return self.__raw_media.media_description.media_type

    @property
    def proto(self):
        """
        There are two objects MediaDescription (media_description as the whole object and the first line of m= in sdp)
        TODO: rename!
        """
        return self.__raw_media.media_description.proto

    @property
    def rtp_codecs(self):
        return self.__sdp_codec_collection.rtp_codecs

    def add_codec(self, codec):
        self.__sdp_codec_collection.add_codec(codec)

    @property
    def direction(self):
        return self.__direction.value

    @direction.setter
    def direction(self, value):
        self.__direction.value = value

    @property
    def ice(self):
        return self.__ice

    @property
    def crypto(self):
        return self.__crypto

    @property
    def streams(self):
        return self.__streams

    @property
    def rtcp_mux(self):
        return self.__rtcp_mux.value

    @rtcp_mux.setter
    def rtcp_mux(self, value):
        assert type(value) is bool
        self.__rtcp_mux.value = value

    @property
    def rtcp(self):
        return self.__rtcp

    @property
    def packet_time(self):
        return self.__ptime.packet_time

    @property
    def silence_supp_enable(self):
        return self.__silence_supp.silence_supp_enable

    @silence_supp_enable.setter
    def silence_supp_enable(self, silence_supp_enable):
        self.__silence_supp.silence_supp_enable = silence_supp_enable

    @packet_time.setter
    def packet_time(self, packet_time):
        assert packet_time is None or type(packet_time) is int
        self.__ptime.packet_time = packet_time

    @property
    def raw_media(self):
        """

        :rtype : raw.media.Media
        """
        return self.__raw_media

    @property
    def mid(self):
        return self.__mid.value if self.__mid else None

    @mid.setter
    def mid(self, mid):
        assert type(mid) is str
        self.__mid.value = mid

    @property
    def host(self):
        if self.__raw_media.connection_data:
            return self.__raw_media.connection_data.connection_address
        else:
            return self.__parent_sdp.host

    @property
    def rtp_port(self):
        return self.__raw_media.media_description.port

    @rtp_port.setter
    def rtp_port(self, rtp_port):
        assert type(rtp_port) is int
        self.__raw_media.media_description.port = rtp_port

    @property
    def rtcp_port(self):
        if self.__rtcp:
            return self.__rtcp.port
        else:
            return self.rtp_port + 1

    @rtcp_port.setter
    def rtcp_port(self, rtcp_port):
        self.__rtcp.port = rtcp_port

    @property
    def connection_data(self):
        return self.__raw_media.connection_data

    @connection_data.setter
    def connection_data(self, connection_data):
        self.__raw_media.connection_data = connection_data

    #
    #
    #
    def add_attribute(self, name, value):
        self.__raw_media.add_attribute(name, value)

    #
    #
    #
    def get_remote_host_port(self):
        port = self.__raw_media.media_description.port
        if self.__raw_media.connection_data:
            host = self.__raw_media.connection_data.connection_address
        else:
            host = self.__parent_sdp.get_remote_host()
        return host, port

    def __str__(self):
        return str(self.__raw_media)

    def add_candidate(self, port=0, host="127.0.0.1"):
        #a=candidate:2896278100 1 udp 2113937151 192.168.1.36 65249 typ host generation 0
        uname_hash = "2896278100"

        self.__raw_media.attributes.append(raw.attribute.Attribute("candidate", raw.attribute.StrAttributeValue(
            uname_hash + " 1 udp 2113937151 " + host + " " + str(port) + " typ srflx generation 0")))
        self.__raw_media.attributes.append(raw.attribute.Attribute("candidate", raw.attribute.StrAttributeValue(
            uname_hash + " 2 udp 2113937151 " + host + " " + str(port) + " typ srflx generation 0")))

    def set_addr(self, port, host=None):
        assert type(port) is int
        assert host is None or type(host) is str
        self.__raw_media.media_description.port = port
        if host is not None:
            if self.__raw_media.connection_data is None:
                self.__raw_media.connection_data = raw.entity.ConnectionData(NetType.IN, AddrType.IP4, host)
            self.__raw_media.connection_data.connection_address = host
        else:
            if self.__raw_media.connection_data is not None:
                self.__raw_media.connection_data = None
