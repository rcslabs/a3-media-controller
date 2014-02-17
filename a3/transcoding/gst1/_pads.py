#!/usr/bin/env python
"""
Gstreamer-1 based implementation of IMediaSource and IMediaDestination

"""


__author__ = 'esix'


import collections

from ...media import ICodec, RawCodec

from .._base import IMediaSource, IMediaDestination
from ._base import Gst


class _MediaPromise(object):
    def __init__(self):
        self.__listeners = []
        self.__value = None
        self.__resolved = False

    def subscribe(self, listener):
        if self.__resolved:
            listener(self.__value)
        else:
            self.__listeners.append(listener)

    def resolve(self, value):
        self.__value = value
        self.__resolved = True
        for listener in self.__listeners:
            listener(value)
        self.__listeners = []


class VirtualMediaSource(IMediaSource, _MediaPromise):
    def __init__(self):
        _MediaPromise.__init__(self)


class VirtualMediaDestination(IMediaDestination, _MediaPromise):
    def __init__(self):
        _MediaPromise.__init__(self)


class MediaSource(VirtualMediaSource):
    def __init__(self, pad, codec):
        assert isinstance(pad, Gst.Pad)
        assert isinstance(codec, ICodec)
        assert pad.get_direction() == Gst.PadDirection.SRC

        self.__pad = pad
        self.__codec = codec

        super(MediaSource, self).__init__()
        self.resolve(self)

    @property
    def gst_pad(self):
        return self.__pad

    @property
    def codec(self):
        return self.__codec

    def is_raw(self):
        return type(self.__codec) is RawCodec

    def __str__(self):
        return "MediaSource [%s]" % str(self.__codec)


class MediaDestination(VirtualMediaDestination):
    def __init__(self, pad, acceptable_codecs):
        assert isinstance(pad, Gst.Pad)
        assert isinstance(acceptable_codecs, collections.Iterable)
        assert False not in list([isinstance(codec, ICodec) for codec in acceptable_codecs])
        assert pad.get_direction() == Gst.PadDirection.SINK

        self.__pad = pad
        self.__acceptable_codecs = acceptable_codecs

        super(MediaDestination, self).__init__()
        self.resolve(self)

    @property
    def gst_pad(self):
        return self.__pad

    @property
    def acceptable_codecs(self):
        return self.__acceptable_codecs

    def accepts(self, codec):
        assert isinstance(codec, ICodec)
        return codec in self.__acceptable_codecs

    def accepts_raw(self):
        for codec in self.__acceptable_codecs:
            if type(codec) is RawCodec:
                return True
        return False

    def __str__(self):
        return "MediaDestination [%s]" % (", ".join([str(codec) for codec in self.__acceptable_codecs]))
