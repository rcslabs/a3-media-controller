#!/usr/bin/env python
"""
declares PtCodecCollection


TODO:
    make it sorted (as list of tuples)


opus/48000/2 (111)
ISAC/16000/1 (103)
ISAC/32000/1 (104)
G722/16000/1 (9)
ILBC/8000/1 (102)
PCMU/8000/1 (0)
PCMA/8000/1 (8)
CN/32000/1 (106)
CN/16000/1 (105)
CN/8000/1 (13)
red/8000/1 (127)
telephone-event/8000/1 (126)


"""

__author__ = 'RCSLabs'


from ._media_type import MediaType
from ._codec import Codec


"""class PtCodecCollection(object):
    def __init__(self, pt_iterable=None):
        self.__pt_map = {}
        if pt_iterable is not None:
            for (pt, codec) in pt_iterable:
                self.add(pt, codec)

    @property
    def payload_types(self):
        return self.__pt_map.keys()

    @property
    def codecs(self):
        return self.__pt_map.values()

    def has_pt(self, pt):
        assert type(pt) is int
        return pt in self.payload_types

    def has_codec(self, codec):
        assert type(codec) is Codec
        return codec in self.codecs

    def add(self, pt, codec):
        assert type(pt) is int
        assert type(codec) is Codec
        self.__pt_map[pt] = codec

    def get_pt(self, codec):
        assert type(codec) is Codec
        for pt, c in self:
            if c == codec:
                return pt
        # TODO: raise exception
        return None

    def get_codec(self, payload_type):
        assert type(payload_type) is int
        for pt, c in self:
            if pt == payload_type:
                return c
        # TODO: raise exception
        return None

    def filter_by_media_type(self, media_type):
        assert type(media_type) is MediaType
        return PtCodecCollection([(pt, codec) for (pt, codec) in self if codec.media_type is media_type])

    def filter_by_codec_collection(self, codec_collection):
        # assert `in`
        return PtCodecCollection([(pt, codec) for (pt, codec) in self if codec in codec_collection])

    def __iter__(self):
        return self.__pt_map.iteritems()

    def __str__(self):
        return ", ".join(["%d: %s" % (pt, str(codec)) for (pt, codec) in self])

    def __len__(self):
        return len(self.__pt_map)

    def first(self):
        key = self.__pt_map.keys()[0]
        return key, self.__pt_map[key]
"""