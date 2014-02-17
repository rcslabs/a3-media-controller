#! /usr/bin/env python
"""

"""

__author__ = 'RCSLabs'

from ...logging import LOG
from ...config.profile import Profile
from ...media import MediaType, Codec, RtpCodec
from .._base import IRtpFrontend
from ..rtp_socket_pair import RtpSocketPair

from .gst_elements import *
from ._pads import MediaSource, MediaDestination, VirtualMediaSource, VirtualMediaDestination
from ._endec import RTP_CAPS, create_depay, create_pay


import re


def get_caps_for_rtp_codec(rtp_codec):
    assert type(rtp_codec) is RtpCodec
    codec = rtp_codec.base_codec
    assert codec in RTP_CAPS
    return Gst.caps_from_string(RTP_CAPS[codec])


class RtpFrontend(IRtpFrontend):
    def __init__(self, media_type, profile):
        from .factory import Gst1TranscodingFactory
        assert type(media_type) is MediaType
        assert type(profile) is Profile

        self.__media_type = media_type
        self.__local_codec = None
        #self.__remote_codec = None
        self.__remote_rtp_codecs = None

        self.__conn = RtpSocketPair(profile, Gst1TranscodingFactory())

        self.__bin = GstBin()
        self.__rtp_bin = RtpBin(pad_added=self.pad_added, request_pt_map=self.request_pt_map)
        self.__bin.add(self.__rtp_bin)
        self.__rtp_sink = None
        self.__rtcp_sink = None
        self.__rtp_src = None
        self.__rtcp_src = None
        self.__fakesink = None

        self.__depay = None
        self.__pay = None

        self.__media_source = VirtualMediaSource()
        self.__media_destination = VirtualMediaDestination()

    #
    # IMediaSourceProvider
    #
    def get_media_source(self):
        return self.__media_source

    #
    # IMediaDestinationProvider
    #
    def get_media_destination(self):
        return self.__media_destination

    @property
    def gst_element(self):
        return self.__bin

    @property
    def ssrc_id(self):
        return self.__rtp_bin.ssrc

    @ssrc_id.setter
    def ssrc_id(self, ssrc_id):
        assert type(ssrc_id) is long
        self.__rtp_bin.ssrc = ssrc_id

    @property
    def cname(self):
        return self.__rtp_bin.cname

    @cname.setter
    def cname(self, cname):
        assert type(cname) is str
        self.__rtp_bin.cname = cname

    def pad_added(self, obj, pad, param):
        pad_name = pad.get_name()
        LOG.debug("Transcoder::pad_added %s", repr(pad_name))

        if "recv_rtp_src_" in pad_name:
            g = re.match("^recv_rtp_src_(\d+)_(\d+)_(\d+)$", pad_name)
            assert g
            #pad_id = int(g.group(1))
            #ssrc_id = long(g.group(2))
            payload_type =  int(g.group(3))
            LOG.debug("RtpFrontend: got remote media pt=%d", payload_type)
            rtp_codecs = [c for c in self.__remote_rtp_codecs if c.payload_type == payload_type]
            assert len(rtp_codecs) == 1
            self.__create_depay(rtp_codecs[0], pad)

    def request_pt_map(self, obj, _, pt, extra):
        LOG.debug("RtpFrontend: request_pt_map on pt=%d", pt)
        rtp_codecs = [c for c in self.__remote_rtp_codecs if c.payload_type == pt]
        assert len(rtp_codecs) == 1
        LOG.debug("RtpFrontend: request_pt_map on pt=%d: result: %s", pt, str(rtp_codecs[0]))
        return get_caps_for_rtp_codec(rtp_codecs[0])

    def force_key_unit(self):
        if self.__depay and self.__media_type is MediaType.VIDEO:
            s = Gst.Structure.new_empty("GstForceKeyUnit")
            s.set_value('all-headers', True)
            e = Gst.Event.new_custom(Gst.EventType.CUSTOM_UPSTREAM, s)
            self.__depay.sink_pad.push_event(e)

    @property
    def rtp_port(self):
        return self.__conn.rtp_port

    @property
    def rtcp_port(self):
        return self.__conn.rtcp_port

    def stop(self):
        pass

    def create_sender(self, local_rtp_codecs, remote_host, remote_rtp_port, remote_rtcp_port):
        """
        creates two udpsink element - for rtp and rtcp
        currently here the codec is selected (as the first one)
        """
        #assert type(local_pt_codec_collection) is PtCodecCollection
        assert type(remote_host) is str
        assert type(remote_rtp_port) is int
        assert type(remote_rtcp_port) is int
        assert len(local_rtp_codecs) >= 1

        assert self.__rtp_sink is None
        assert self.__rtcp_sink is None

        local_rtp_codec = local_rtp_codecs[0]

        LOG.debug("RtpTranscoder.create_sender %s -> %s:%d,%d",
                  local_rtp_codec, remote_host, remote_rtp_port, remote_rtcp_port)
        self.__local_codec = local_rtp_codec

        self.__rtp_sink = UdpSink(socket=self.__conn.rtp_socket, host=remote_host, port=remote_rtp_port)
        self.__rtcp_sink = UdpSink(socket=self.__conn.rtcp_socket, host=remote_host, port=remote_rtcp_port)
        self.__bin.add(self.__rtp_sink)
        self.__bin.add(self.__rtcp_sink)
        self.__rtp_bin._element.get_static_pad("send_rtp_src_0").link(self.__rtp_sink.sink_pad)
        self.__rtp_bin._element.get_request_pad("send_rtcp_src_0").link(self.__rtcp_sink.sink_pad)

        self.__create_pay(local_rtp_codec)

    def create_receiver(self, remote_rtp_codecs):
        """
        creates two udpsrc element - for rtp and rtcp
        """
        #assert type(remote_pt_codec_collection) is PtCodecCollection
        assert self.__rtp_src is None
        assert self.__rtcp_src is None
        self.__remote_rtp_codecs = remote_rtp_codecs

        self.__rtp_src = UdpSrc(socket=self.__conn.rtp_socket)
        self.__rtcp_src = UdpSrc(socket=self.__conn.rtcp_socket)

        self.__bin.add(self.__rtp_src)
        self.__bin.add(self.__rtcp_src)

        rtp_sink_pad = self.__rtp_bin._element.get_request_pad("recv_rtp_sink_0")
        assert rtp_sink_pad
        rtp_src_pad = self.__rtp_src.src_pad
        assert rtp_src_pad
        rtp_src_pad.link(rtp_sink_pad)

        rtcp_sink_pad = self.__rtp_bin._element.get_request_pad("recv_rtcp_sink_0")
        assert rtcp_sink_pad
        rtcp_src_pad = self.__rtcp_src.src_pad
        assert rtcp_src_pad
        rtcp_src_pad.link(rtcp_sink_pad)

    def __create_depay(self, remote_codec, pad):
        """
        creates decoder of remote media
        it's remote media, and we use remote-media to decode it
        """
        assert type(remote_codec) is RtpCodec
        self.__depay = create_depay(remote_codec)
        self.__bin.add(self.__depay)
        pad.link(self.__depay.sink_pad)

        src_pad = Gst.GhostPad.new("src", self.__depay.src_pad)
        src_pad.set_active(True)
        self.__bin._element.add_pad(src_pad)

        self.__media_source.resolve(MediaSource(src_pad, remote_codec.base_codec))

    def __create_pay(self, local_rtp_codec):
        """
        creates encoder element for destination
        it's our media and we use our local-media to encode it
        """
        assert type(local_rtp_codec) is RtpCodec

        self.__pay = create_pay(local_rtp_codec)
        self.__bin.add(self.__pay)
        self.__pay.src_pad.link(self.__rtp_bin._element.get_static_pad("send_rtp_sink_0"))

        sink_pad = Gst.GhostPad.new("sink", self.__pay.sink_pad)
        sink_pad.set_active(True)
        self.__bin._element.add_pad(sink_pad)

        self.__media_destination.resolve(MediaDestination(sink_pad, [local_rtp_codec.base_codec]))

    def dispose(self):
        assert self.__conn is not None
        self.__conn.close()
        self.__conn = None
