#! /usr/bin/env python
"""


gst-launch-1.0 --gst-debug=4 videotestsrc  ! "video/x-raw,format=(string)YUY2,width=(int)352,height=(int)288,pixel-aspect-ratio=(fraction)1/1,framerate=(fraction)15/1" ! videoconvert ! x264enc bitrate=300 pass=pass1 speed-preset=1 byte-stream=true !  flvmux streamable=true ! rtmpsink location="rtmp://192.168.1.200/live/pubvideo live=1"



---gst-launch-1.0 --gst-debug=3 rtmpsrc location="rtmp://192.168.1.200/live/subvideo live=1" ! decodebin ! videoconvert ! ximagesink


gst-launch-1.0 --gst-debug=3 rtmpsrc location="rtmp://192.168.1.200/live/subvideo live=1" ! flvdemux ! avdec_flv ! videoconvert ! ximagesink


"""

__author__ = 'RCSLabs'


from ...logging import LOG
from ...config.profile import Profile
from ...media import MediaType, Codec, RtpCodec, CODEC
from .._base import IRtmpFrontend
from ..rtp_socket_pair import RtpSocketPair

from ._elements import *
from ._pads import MediaSource, MediaDestination, VirtualMediaSource, VirtualMediaDestination
from ._endec import RTP_CAPS, create_depay, create_pay

import time

import re


class RtmpFrontend(IRtmpFrontend):
    def __init__(self, media_type, profile):
        assert type(media_type) is MediaType
        assert type(profile) is Profile
        self.__media_type = media_type

        self.__remote_codec = None
        self.__local_codec = None

        self.__context = None

        self.__bin = GstBin()
        # self.__bin._element = Gst.parse_bin_from_description("""
        #     rtmpsrc location="rtmp://192.168.1.200/live/subaudio live=1" !
        #     flvdemux ! speexdec ! audioresample !
        #     capsfilter caps="audio/x-raw, format=(string)S16LE, rate=(int)8000" """, True)
        #
        # self.__media_source = MediaSource(self.__bin._element.get_static_pad("src"), CODEC.RAW_AUDIO)
        # self.__media_destination = VirtualMediaDestination()

        #
        # receiver
        #
        self.__src = Gst.ElementFactory.make("rtmpsrc", None)
        self.__src.set_property("location", self.sub + " live=1")
        self.__bin.element.add(self.__src)

        self.__demux = Gst.ElementFactory.make("flvdemux", None)
        self.__demux.connect("pad-added", self.__flvdemux_audio_pad_added, None)
        self.__bin.element.add(self.__demux)

        self.__src.get_static_pad("src").link(self.__demux.get_static_pad("sink"))

        #
        # sender
        #
        if media_type is MediaType.AUDIO:
            # self.__sender = Gst.parse_bin_from_description("""
            #     audioresample !
            #     audio/x-raw,format=(string)S16LE,layout=interleaved,rate=5512,channels=1 !
            #     flvmux streamable=true !
            #     rtmpsink location="%s live=1"
            # """ % (self.pub,), True)
            self.__sender = Gst.parse_bin_from_description("""
                queue !
                audio/x-raw,format=(string)S16LE,layout=interleaved,rate=8000,channels=1 !
                audioconvert ! avenc_nellymoser !
                flvmux streamable=true !
                rtmpsink location="%s live=1"
            # """ % (self.pub,), True)
        else:
            #    videoconvert ! x264enc bitrate=300 pass=pass1 speed-preset=1 byte-stream=true !
            self.__sender = Gst.parse_bin_from_description("""
                queue !
                flvmux streamable=true !
                rtmpsink location="%s live=1"
            """ % (self.pub,), True)

        self.__bin.element.add(self.__sender)
        sink_pad = Gst.GhostPad.new("sink", self.__sender.get_static_pad("sink"))
        sink_pad.set_active(True)
        self.__bin.element.add_pad(sink_pad)

        self.__media_source = VirtualMediaSource()
        if media_type is MediaType.AUDIO:
            self.__media_destination = MediaDestination(sink_pad, [CODEC.RAW(media_type)])
        else:
            self.__media_destination = MediaDestination(sink_pad, [CODEC.H264])

        self.__bin.element.set_state(Gst.State.PAUSED)

    def set_context(self, context):
        assert context is None or type(context) is GstPipeline

        if self.__context is context:
            return

        if self.__context:
            self.__context.remove(self.__bin)

        self.__context = context

        if self.__context:
            self.__context = context
            self.__context.add(self.__bin)
            #self.__bin.element.sync_state_with_parent()

    @property
    def sub(self):
        return "rtmp://192.168.1.200/live/sub" + self.__media_type

    @property
    def pub(self):
        return "rtmp://192.168.1.200/live/pub" + self.__media_type

    def dispose(self):
        pass

    def force_key_unit(self):
        pass

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

    #
    # private
    #
    def __flvdemux_audio_pad_added(self, obj, flvdemux_src_pad, param):
        print "\n\n\n\n\n\nPAD ADDED\n", obj, flvdemux_src_pad, param, "\n", flvdemux_src_pad.get_property("name"), "\n\n\n\n\n\n\n\n"
        if self.__media_type is MediaType.AUDIO:
            p = self.__bin.element

            # b = Gst.parse_bin_from_description("""queue ! speexdec ! audioresample !
            #                                       audio/x-raw,format=(string)S16LE,rate=(int)8000,channels=1 !
            #                                       audiorate""", True)

            b = Gst.parse_bin_from_description("""queue ! avdec_nellymoser  ! audioresample !
                                                  audio/x-raw,format=F32LE,layout=interleaved,rate=8000,channels=1 !
                                                  audioconvert !
                                                  audio/x-raw,format=S16LE,rate=8000,channels=1 !
                                                  audiorate""", True)

            p.add(b)
            b.sync_state_with_parent()

            src_pad = Gst.GhostPad.new("src", b.get_static_pad("src"))
            src_pad.set_active(True)
            p.add_pad(src_pad)
            self.__media_source.resolve(MediaSource(src_pad, CODEC.RAW(self.__media_type)))

            flvdemux_src_pad.link(b.get_static_pad("sink"))

        else:   # MediaType.VIDEO
            p = self.__bin.element

            #b = Gst.parse_bin_from_description("""queue ! avdec_flv ! videoconvert """, True)
            b = Gst.parse_bin_from_description("""queue ! h264parse """, True)

            p.add(b)
            b.sync_state_with_parent()

            src_pad = Gst.GhostPad.new("src", b.get_static_pad("src"))
            src_pad.set_active(True)
            p.add_pad(src_pad)
            #self.__media_source.resolve(MediaSource(src_pad, CODEC.RAW(self.__media_type)))
            self.__media_source.resolve(MediaSource(src_pad, CODEC.H264))

            flvdemux_src_pad.link(b.get_static_pad("sink"))


if __name__ == "__main__":
    #
    # python -m a3.transcoding.gst1._rtmp_fromtend
    #

    # gst-launch-1.0 --gst-debug=3 rtmpsrc location="rtmp://192.168.1.200/live/subaudio live=1" ! flvdemux ! audio/x-speex,rate=5512 ! speexdec ! alsasink

    from _base import Gst, GObject
    p = Gst.Pipeline()

    print "Creating pipeline"

    def pad_added(obj, pad, param):
        print "\n\n\n\n\n\nPAD ADDED\n\n\n\n\n\n\n\n", obj, pad, param

        sink = Gst.ElementFactory.make("alsasink", None)
        speexdec = Gst.ElementFactory.make("speexdec", None)
        #caps = Gst.ElementFactory.make("capsfilter", None)
        #caps.set_property("caps", Gst.caps_from_string("audio/x-speex,rate=5512"))

        p.add(sink)
        p.add(speexdec)
        #p.add(caps)

        sink.sync_state_with_parent()
        speexdec.sync_state_with_parent()
        #caps.sync_state_with_parent()

        speexdec.link(sink)
        #caps.link(speexdec)

        pad.link(speexdec.get_static_pad("sink"))
        p.set_state(Gst.State.PLAYING)


    src = Gst.ElementFactory.make("rtmpsrc", None)
    src.set_property("location", "rtmp://192.168.1.200/live/subaudio live=1")
    p.add(src)
    src.sync_state_with_parent()

    flvdemux = Gst.ElementFactory.make("flvdemux", None)
    flvdemux.connect("pad-added", pad_added, None)
    p.add(flvdemux)
    flvdemux.sync_state_with_parent()

    src.link(flvdemux)

    print "Starting"
    p.set_state(Gst.State.PAUSED)

    mainloop = GObject.MainLoop()
    mainloop.run()
