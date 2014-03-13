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
from ._elements import GstPipeline

import threading
import time


DTMF_DURATION = 0.35
DTMF_PAUSE = 0.05


class DtmfSender(IDtmfSender, threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True

        self.__context = None
        self.__is_terminated = True

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
        dtmf_numbers = {
            '0': 0,  '1': 1,  '2': 2,  '3': 3,
            '4': 4,  '5': 5,  '6': 6,  '7': 7,
            '8': 8,  '9': 9,  '*': 10, '#': 11,
            'A': 12, 'B': 13, 'C': 14, 'D': 15
        }
        for c in dtmf:
            if c in dtmf_numbers:
                self.__dtmf_buffer.append(dtmf_numbers[c])
        self.__send_dtmf_event.set()

    def set_context(self, context):
        assert context is None or type(context) is GstPipeline

        if self.__context is context:
            return

        if self.__context:
            self.__context._element.remove(self.__dtmfsrc)
            self.__context._element.remove(self.__input_selector)

        self.__context = context

        if self.__context:
            self.__context._element.add(self.__input_selector)
            self.__context._element.add(self.__dtmfsrc)
            self.__dtmfsrc.get_static_pad("src").link(self.__dtmf_destination_pad)

    def start(self):
        return super(DtmfSender, self).start()

    def stop(self):
        if not self.__is_terminated:
            self.__is_terminated = True
            self.__send_dtmf_event.set()
            self.join()

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
        self.__is_terminated = False
        self.__dtmf_thread_cycle()
        LOG.info("DTMF thread stopped")
        self.__is_terminated = True

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
        assert type(sign) is int
        s = Gst.Structure.new_empty("dtmf-event")
        s.set_value('type', 1)
        s.set_value('number', sign)
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
