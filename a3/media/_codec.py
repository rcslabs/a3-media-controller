#!/usr/bin/env python
"""
Codec description
"""

from ._media_type import MediaType
from abc import ABCMeta, abstractproperty, abstractmethod


DEFAULT_CHANNELS = 1


class ICodec(object):
    __metaclass__ = ABCMeta

    @abstractproperty
    def media_type(self):
        """
        return media type of codec
        """

    @abstractmethod
    def clone(self):
        """
        return copy of codec
        """


class RawCodec(ICodec):
    def __init__(self, media_type):
        assert type(media_type) is MediaType
        self.__media_type = media_type

    @property
    def media_type(self):
        return self.__media_type

    def __str__(self):
        return "RAW"

    def __hash__(self):
        return hash(self.__media_type)

    def __eq__(self, other):
        return type(other) is RawCodec and self.media_type == other.media_type

    def __ne__(self, other):
        return not (self == other)

    def clone(self):
        return RawCodec(self.__media_type)


class Codec(ICodec):
    def __init__(self, media_type, encoding_name, clock_rate, channels):
        assert type(media_type) is MediaType
        assert type(encoding_name) is str
        assert type(clock_rate) is int
        assert type(channels) is int

        self._media_type = media_type
        self.__encoding_name = encoding_name
        self.__clock_rate = clock_rate
        self.__channels = channels or DEFAULT_CHANNELS

    @property
    def encoding_name(self):
        return self.__encoding_name

    @property
    def clock_rate(self):
        return self.__clock_rate

    @property
    def channels(self):
        return self.__channels

    @property
    def media_type(self):
        return self._media_type

    def clone(self):
        return Codec(self._media_type,
                     self.__encoding_name,
                     self.__clock_rate,
                     self.__channels)

    def __str__(self):
        return "%s/%d" % (self.__encoding_name, self.__clock_rate) + (
            "/" + str(self.__channels) if self.__channels != 2 else "")

    def __hash__(self):
        return hash((self.media_type, self.__encoding_name, self.__clock_rate, self.__channels))

    def __eq__(self, other):
        return type(other) is Codec and (self.__encoding_name, self.__clock_rate, self.__channels) == \
            (other.__encoding_name, other.__clock_rate, other.__channels)

    def __ne__(self, other):
        return not (self == other)


class RtpCodec(ICodec):
    """
    TODO: redefine __eq__
    also fix Codec::__eq__
    """

    def __init__(self, base_codec, payload_type):
        assert type(base_codec) is Codec
        assert type(payload_type) is int
        self.__base_codec = base_codec
        self.__payload_type = payload_type

    @property
    def media_type(self):
        return self.__base_codec.media_type

    @property
    def payload_type(self):
        return self.__payload_type

    @property
    def encoding_name(self):
        return self.__base_codec.encoding_name

    @property
    def clock_rate(self):
        return self.__base_codec.encoding_name

    @property
    def channels(self):
        return self.__base_codec.channels

    def clone(self):
        return RtpCodec(self.__base_codec.clone(), self.__payload_type)

    @property
    def base_codec(self):
        return self.__base_codec

    def __str__(self):
        return str(self.__base_codec) + ",pt=" + str(self.__payload_type)

    def __hash__(self):
        return hash((self.__base_codec, self.__payload_type))

    def __eq__(self, other):
        return type(other) is RtpCodec and \
            self.base_codec == other.base_codec and \
            self.payload_type == other.payload_type

    def __ne__(self, other):
        return not (self == other)


def AudioCodec(encoding_name, clock_rate, channels):
    return Codec(MediaType.AUDIO, encoding_name, clock_rate, channels)


def VideoCodec(encoding_name, clock_rate, channels):
    return Codec(MediaType.VIDEO, encoding_name, clock_rate, channels)


class CODEC:
    # audio codecs
    PCMA = AudioCodec("PCMA", 8000, 1)
    PCMU = AudioCodec("PCMU", 8000, 1)
    OPUS = AudioCodec("opus", 48000, 1)
    OPUS2 = AudioCodec("opus", 48000, 2)
    SPEEX = AudioCodec("speex", 48000, 1)
    TELEPHONE_EVENT = AudioCodec("telephone-event", 8000, 1)

    # video codecs
    H264 = VideoCodec("H264", 90000, 1)
    VP8 = VideoCodec("VP8", 90000, 1)
    H263_1998 = VideoCodec("H263-1998", 90000, 1)
    H263 = VideoCodec("H263-1998", 90000, 1)

    # utils
    RAW_AUDIO = RawCodec(MediaType.AUDIO)
    RAW_VIDEO = RawCodec(MediaType.VIDEO)

    @classmethod
    def RAW(cls, media_type):
        assert type(media_type) is MediaType
        if media_type is MediaType.AUDIO:
            return cls.RAW_AUDIO
        elif media_type is MediaType.VIDEO:
            return cls.RAW_VIDEO
        else:
            raise Exception("Unknown message type")


if __name__ == "__main__":
    import unittest

    class CodecNameTest(unittest.TestCase):
        def test_compare(self):
            PCMA = Codec(MediaType.AUDIO, "PCMA", 8000, 1)
            self.failUnlessEqual(CODEC.PCMA, PCMA)
            VP8_2 = Codec(MediaType.AUDIO, "PCMA", 8000, 2)
            self.failIfEqual(CODEC.VP8, VP8_2)
            h = {
                CODEC.PCMA: "Codec1",
                CODEC.VP8: "Codec2"
            }
            self.failUnlessEqual(h[PCMA], "Codec1")
            self.failUnlessEqual(h[Codec(MediaType.VIDEO, "VP8", 90000, 1)], "Codec2")
            assert Codec(MediaType.AUDIO, "PCMA", 8000, 1) in h
            assert Codec(MediaType.AUDIO, "PCMA", 8000, 1) in h.keys()
            try:
                h[Codec(MediaType.AUDIO, "PCMU", 8000, 1)]
                self.fail("Did not see KeyError")
            except KeyError:
                pass

        def test_str(self):
            self.failUnlessEqual(str(CODEC.PCMU), "PCMU/8000")
            self.failUnlessEqual(str(Codec(MediaType.VIDEO, "VP8", 90000, 4)), "VP8/90000/4")

        def test_set(self):
            c1 = {CODEC.PCMA, CODEC.PCMU}
            PCMA = Codec(MediaType.AUDIO, "PCMA", 8000, 1)
            if PCMA not in c1:
                self.fail("PCMA not in c")

            c2 = {Codec(MediaType.AUDIO, "PCMU", 8000, 1), CODEC.VP8}
            intercept = c1 & c2
            assert len(intercept) == 1
            assert list(intercept)[0] == Codec(MediaType.AUDIO, "PCMU", 8000, 1)

    unittest.main()
