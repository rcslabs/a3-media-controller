#!/usr/bin/env python
"""
Transcoding implementation using gstreamer-0.10


"""

__author__ = 'RCSLabs'


from .._base import ITranscodingFactory
from ._socket import Socket as _Socket


class Gst10TranscodingFactory(ITranscodingFactory):
    """
    Implements TranscodingFactory methods
    """
    def create_socket(self, port, interface="0.0.0.0"):
        return _Socket(port, interface)

    def create_udp_sink(self, socket):
        #
        #TODO: implement gst 10 bases udp sink
        #
        pass

