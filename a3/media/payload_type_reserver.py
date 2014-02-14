#!/usr/bin/env python


from ._codec import Codec, RtpCodec
#from ._pt_codec_collection import PtCodecCollection
from ._known_pt_codecs import KNOWN_RTP_CODECS


DYNAMIC_PT = xrange(96, 127)

"""
class PayloadTypeReserverError(Exception):
    def __init__(self, value):
        assert type(value) is str
        self.value = value

    def __str__(self):
        return str(self.value)


class PayloadTypeReserver(object):
    def __init__(self):
        self.__pt_codec_collection = PtCodecCollection()

    @property
    def pt_codec_collection(self):
        return self.__pt_codec_collection

    def is_codec_reserved(self, codec):
        assert type(codec) is Codec
        return self.__pt_codec_collection.has_codec(codec)

    def is_pt_reserved(self, payload_type):
        assert type(payload_type) is int
        return self.__pt_codec_collection.has_pt(payload_type)

    def __reserve_with_payload_type(self, codec, payload_type):
        assert type(codec) is Codec
        assert type(payload_type) is int

        if self.is_pt_reserved(payload_type):
            reserved_codec = self.__pt_codec_collection.get_codec(payload_type)
            if reserved_codec != codec:
                raise PayloadTypeReserverError("Payload type %d already reserved" % (payload_type,))
        else:
            self.__pt_codec_collection.add(payload_type, codec)

    def reserve_rtp_codec(self, rtp_codec):
        assert type(rtp_codec) is RtpCodec

    def reserve_codec(self, codec, payload_type=None):
        assert type(codec) is Codec
        assert payload_type is None or type(payload_type) is int

        #
        # Try to reserve when a payload type is set
        #
        if payload_type is not None:
            self.__reserve_with_payload_type(codec, payload_type)
            return payload_type

        #
        # If codec is already in collection we return its payload type
        #
        if self.is_codec_reserved(codec):
            return self.__pt_codec_collection.get_pt(codec)

        #
        # If codec is standard and its standard payload type is not reserved
        #  register it and and return that payload type
        #
        if KNOWN_PT_CODECS.has_codec(codec) and not self.is_pt_reserved(KNOWN_PT_CODECS.get_pt(codec)):
            pt = KNOWN_PT_CODECS.get_pt(codec)
            self.__reserve_with_payload_type(codec, pt)
            return pt

        #
        # Find free payload type, reserve it for codec and return
        #
        for pt in DYNAMIC_PT:
            if not self.is_pt_reserved(pt):
                self.__reserve_with_payload_type(codec, pt)
                return pt

        raise PayloadTypeReserverError("Too many codecs for payload type dynamic range")

"""

if __name__ == "__main__":
    import unittest

    PCMU = Codec("PCMU",  8000)
    PCMA = Codec("PCMA",  8000)
    H263 = Codec("H263",  90000)
    H264 = Codec("H264",  90000)
    VP8 = Codec("VP8",  90000)

    class PayloadTypeReserverTest(unittest.TestCase):
        def test_defaults(self):
            p = PayloadTypeReserver()
            self.failUnlessEqual(p.get_pt(PCMU), 0)
            self.failUnlessEqual(p.get_pt(PCMA), 8)
            self.failUnlessEqual(p.get_codec(0), PCMU)
            self.failUnlessEqual(p.get_codec(8), PCMA)

            self.failUnlessRaises(PayloadTypeReserverError, p.get_codec, 96)
            self.failUnlessEqual(p.get_pt(H264), 96)
            self.failUnlessEqual(p.get_codec(96), H264)

        def test_includes(self):
            p = PayloadTypeReserver()
            self.failIf(H264 in p)
            self.failIf(96 in p)
            p.get_pt(H264)
            self.failUnless(H264 in p)
            self.failUnless(96 in p)

        def test_replace(self):
            p = PayloadTypeReserver()
            p.save(8, Codec("VP8", 90000))
            self.failUnlessEqual(p.get_pt(Codec("VP8", 90000)), 8)
            self.failUnlessEqual(p.get_codec(8), Codec("VP8", 90000))

            p.save(0, Codec("VP9", 90000))
            self.failUnlessEqual(p.get_pt(Codec("VP9", 90000)), 0)
            self.failUnlessEqual(p.get_codec(0), Codec("VP9", 90000))


    unittest.main()
