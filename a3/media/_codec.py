#!/usr/bin/env python
"""
Codec description
"""


from ._media_type import MediaType


DEFAULT_CHANNELS = 1


class Codec(object):
    def __init__(self, media_type, encoding_name, clock_rate, channels):
        assert type(media_type) is MediaType
        assert type(encoding_name) is str
        assert type(clock_rate) is int
        assert type(channels) is int

        self._media_type = media_type
        self._encoding_name = encoding_name
        self._clock_rate = clock_rate
        self._channels = channels or DEFAULT_CHANNELS

    @property
    def encoding_name(self):
        return self._encoding_name

    @property
    def clock_rate(self):
        return self._clock_rate

    @property
    def channels(self):
        return self._channels

    @property
    def media_type(self):
        return self._media_type

    def clone(self):
        return Codec(self._media_type,
                     self._encoding_name,
                     self._clock_rate,
                     self._channels)

    def __str__(self):
        return "Codec(%s/%d/%d)" % (self._encoding_name, self._clock_rate, self._channels)

    def __hash__(self):
        return hash((self.media_type, self._encoding_name, self._clock_rate, self._channels))

    def __eq__(self, other):
        assert isinstance(other, Codec)
        return (self._encoding_name, self._clock_rate, self._channels) == \
               (other._encoding_name, other._clock_rate, other._channels)

    def __ne__(self, other):
        return not (self == other)


class RtpCodec(Codec):
    """
    TODO: redefine __eq__
    also fix Codec::__eq__
    """
    def __init__(self, codec, payload_type):
        assert type(codec) is Codec
        assert type(payload_type) is int
        super(RtpCodec, self).__init__(codec.media_type, codec.encoding_name, codec.clock_rate, codec.channels)
        self._payload_type = payload_type

    @property
    def payload_type(self):
        return self._payload_type

    def __str__(self):
        return "RtpCodec(%s/%d/%d pt=%d)" % (self._encoding_name, self._clock_rate, self._channels, self._payload_type)

    @property
    def codec(self):
        return Codec(self._media_type, self._encoding_name, self._clock_rate, self._channels)


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
    RAW_AUDIO = AudioCodec("RAW", 8000, 1)
    RAW_VIDEO = VideoCodec("RAW", 90000, 1)

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
