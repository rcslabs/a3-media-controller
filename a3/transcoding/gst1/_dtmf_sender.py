#!/usr/bin/env python
"""

DtmfSender

TODO:
implement rtp-nte (named telephone events)
RFC2833


"""


__author__ = 'RCSLabs'


from ...logging import LOG
from ...media import CODEC
from .._base import IDtmfSender
from ._base import Gst, GObject
from ._pads import MediaSource, MediaDestination

import threading
import time


DTMF_DURATION = 0.35
DTMF_PAUSE = 0.05


class DtmfSender(IDtmfSender, threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True

        self.__is_terminated = False

        self.__input_selector = Gst.ElementFactory.make("input-selector", None)
        self.__dtmfsrc = Gst.ElementFactory.make("dtmfsrc", None)
        assert self.__input_selector is not None
        assert self.__dtmfsrc is not None

        self.__media_src_pad = self.__input_selector.get_static_pad("src")
        assert self.__media_src_pad is not None

        self.__media_destination_pad = self.__input_selector.get_request_pad("sink_%u")
        assert self.__media_destination_pad is not None

        self.__dtmf_destination_pad = self.__input_selector.get_request_pad("sink_%u")
        assert self.__dtmf_destination_pad is not None

        self.__send_dtmf_event = threading.Event()
        self.__dtmf_buffer = []

        self.__media_source = MediaSource(self.__media_src_pad, CODEC.RAW_AUDIO)
        self.__media_destination = MediaDestination(self.__media_destination_pad, [CODEC.RAW_AUDIO])

    def send_dtmf(self, dtmf):
        assert type(dtmf) is str
        for c in dtmf:
            #
            # TODO: support additional DTMF characters
            #
            if c in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                self.__dtmf_buffer.append(c)
        self.__send_dtmf_event.set()

    def add_to_pipeline(self, pipeline):
        #
        # Pipeline here is gstreamer pipeline
        # TODO: accept Pipeline wrapper
        #
        pipeline.add(self.__input_selector)
        pipeline.add(self.__dtmfsrc)
        self.__dtmfsrc.get_static_pad("src").link(self.__dtmf_destination_pad)

    def remove_from_pipeline(self, pipeline):
        #
        # Pipeline here is gstreamer pipeline
        # TODO: accept Pipeline wrapper
        #
        pipeline.remove(self.__dtmfsrc)
        pipeline.remove(self.__input_selector)

    def start(self):
        return super(DtmfSender, self).start()

    def stop(self):
        self.__is_terminated = True
        self.__send_dtmf_event.set()

    def dispose(self):
        LOG("DtmfSender.dispose")

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
    # threading.Thread
    #
    def run(self):
        self.__dtmf_thread_cycle()
        LOG.info("DTMF thread stopped")

    #
    # private
    #
    def __dtmf_thread_cycle(self):
        while True:
            if len(self.__dtmf_buffer):
                c = self.__dtmf_buffer.pop(0)
                LOG.info("DTMF: Playing %s", c)
                self.__input_selector.set_property("active-pad", self.__dtmf_destination_pad)
                self.__set_silent()
                self.__set_playing(c)
                time.sleep(DTMF_DURATION)
                self.__set_silent()
                time.sleep(DTMF_PAUSE)
            else:
                self.__input_selector.set_property("active-pad", self.__media_destination_pad)
                self.__send_dtmf_event.wait()
                self.__send_dtmf_event.clear()

            if self.__is_terminated:
                return

    def __set_playing(self, sign):
        assert type(sign) is str
        s = Gst.Structure.new_empty("dtmf-event")
        s.set_value('type', 1)
        s.set_value('number', int(sign))
        s.set_value('volume', 25)
        s.set_value('start', True)
        e = Gst.Event.new_custom(Gst.EventType.CUSTOM_UPSTREAM, s)
        self.__dtmf_destination_pad.push_event(e)

    def __set_silent(self):
        s = Gst.Structure.new_empty("dtmf-event")
        s.set_value('type', 1)
        s.set_value('start', False)
        e = Gst.Event.new_custom(Gst.EventType.CUSTOM_UPSTREAM, s)
        self.__dtmf_destination_pad.push_event(e)


if __name__ == "__main__":
    #
    # python -m a3.transcoding.gst1._dtmf_sender
    #

    pipeline = Gst.Pipeline()

    dtmf_sender = DtmfSender()
    sink = Gst.ElementFactory.make("alsasink", None)
    src = Gst.ElementFactory.make("audiotestsrc", None)

    pipeline.add(sink)
    pipeline.add(src)

    src_pad = src.get_static_pad("src")
    sink_pad = sink.get_static_pad("sink")

    dtmf_sender.add_to_pipeline(pipeline)

    def on_get_media_source(i_src_pad):
        def on_get_media_destination(i_sink_pad):
            i_src_pad.link(sink_pad)
            src_pad.link(i_sink_pad)
            print "Starting"
            pipeline.set_state(Gst.State.PLAYING)
            dtmf_sender.start()

            while True:
                print "input dtmf>"
                dtmf = raw_input()
                dtmf_sender.send_dtmf(dtmf)

        dtmf_sender.async_get_media_destination(on_get_media_destination)

    dtmf_sender.async_get_media_source(on_get_media_source)

    mainloop = GObject.MainLoop()
    mainloop.run()