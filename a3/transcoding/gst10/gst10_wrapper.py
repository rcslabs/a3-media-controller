#!/usr/bin/env python

import pygst
pygst.require("0.10")
import gst


class Gst(object):
    class State:
        PLAYING = gst.STATE_PLAYING
        PAUSED = gst.STATE_PAUSED
        NULL = gst.STATE_NULL

    class PadDirection:
        SRC = gst.PAD_SRC
        SINK = gst.PAD_SINK

    class PadPresence(object):
        ALWAYS = gst.PAD_ALWAYS
        REQUEST = gst.PAD_REQUEST
        SOMETIMES = gst.PAD_SOMETIMES

    class ElementFactory(object):
        @classmethod
        def make(cls, element_type, element_name):
            return gst.element_factory_make(element_type, element_name)

    class GhostPad(object):
        @classmethod
        def new(cls, name, pad):
            return gst.GhostPad(name, pad)

    @classmethod
    def Pipeline(cls):
        return gst.Pipeline()

    @classmethod
    def Bin(cls, name=None):
        return gst.Bin(name)

    @classmethod
    def caps_from_string(cls, s):
        return gst.Caps(s)

    @classmethod
    def parse_bin_from_description(cls, s, b):
        return gst.parse_bin_from_description(s, b)
