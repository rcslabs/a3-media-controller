#!/usr/bin/env python
"""
gstreamer-0.10 elements
"""


__author__ = 'esix'


from ...logging import LOG
from .._socket import ISocket


from string import Template
from ._base import gst


H264_DECODE = """rtph264depay ! ffdec_h264"""


class UdpSrc(GstElement):
    def __init__(self, port=0, iface="", caps="", socket=None):
        super(UdpSrc, self).__init__(Gst.ElementFactory.make('udpsrc', None))
        self.__iface = iface
        if socket:
            assert isinstance(socket, ISocket)
            self._element.set_property("sockfd", socket.get_fd())
            self._element.set_property("closefd", False)

        else:
            self._element.set_property("port", port)
        self._element.set_state(Gst.State.PAUSED)

        if caps:
            self.set_caps(caps)

    def set_caps(self, str_caps):
        self._element.set_property("caps", Gst.caps_from_string(str_caps))

    @property
    def port(self):
        return self._element.get_property("port")

    def __str__(self):
        return "[UdpSrc, port: {0}]".format(self.port)


#   def create_filesave_encoder(self):
#       LOG.debug("Creating video filesave encoder")
#       if gst_version == "1.0":
#           bin = Gst.parse_bin_from_description(
#               "queue ! video/x-raw ! videoconvert ! matroskamux ! filesink location=video.mkv", True)
#       else:
#           bin = Gst.parse_bin_from_description(
#               "queue ! video/x-raw-yuv ! ffmpegcolorspace ! matroskamux ! filesink location=video.mkv", True)
#       return bin



####################  gstreamer-0.10 ##########################
#
#VP8_ENCODE = Template("""queue !
#                         videoscale !
#                         video/x-raw-yuv !
#                         videorate !
#                         video/x-raw-yuv,framerate=(fraction)15/1,width=(int)352,height=(int)288 !
#                         vp8enc speed=7 max-keyframe-distance=32 quality=2 !
#                         rtpvp8pay ssrc=$ssrc pt=$pt""")
#
#VP8_DECODE = """rtpvp8depay ! vp8dec ! ffmpegcolorspace"""
#
#H264_ENCODE = Template("""queue !
#                          videorate !
#                          video/x-raw-yuv,framerate=15/1 !
#                          x264enc byte-stream=true bitrate=300 pass=5 speed-preset=1 !
#                          rtph264pay ssrc=$ssrc pt=$pt""")
#
#SRC_PAD_NAME = 'src%d'
#SEND_RTP_SINK_PAD = "send_rtp_sink_%d"
#
#VIDEO_TEST_SRC = "videotestsrc pattern=18 ! video/x-raw-rgb,framerate=(fraction)15/1,width=(int)352,height=(int)288 ! queue"
#
#AUDIO_TEST_SRC = "audiotestsrc ! queue"
#
#RTPBIN = "gstrtpbin"
#
###############################################################

