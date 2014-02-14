#! /usr/bin/env python
"""
Gstreamer-1 based transcoding factory implementation
"""


__author__ = 'RCSLabs'

from .._base import ITranscodingFactory
from ._socket import Socket as _Socket
from _dtmf_sender import DtmfSender as _DtmfSender
from ._rtp_frontend import RtpFrontend as _RtpFrontend
from ._endec import RTP_CAPS
from ._link import Link as _Link
from .gst_elements import *


class _Gst1TranscodingFactoryImpl(ITranscodingFactory):
    """
    Implements TranscodingFactory methods
    """
    def create_socket(self, port, interface="0.0.0.0"):
        return _Socket(port, interface)

    def create_rtp_frontend(self, media_type, profile):
        return _RtpFrontend(media_type, profile)

    def create_transcoding_context(self):
        return GstPipeline()

    def create_inband_dtmf_sender(self):
        return _DtmfSender()

    def create_link(self, context, media_source, media_destination):
        return _Link(context, media_source, media_destination)

    def get_supported_codecs(self):
        return RTP_CAPS.keys()


_instance = None


def Gst1TranscodingFactory():
    global _instance
    if _instance is None:
        _instance = _Gst1TranscodingFactoryImpl()
    return _instance
