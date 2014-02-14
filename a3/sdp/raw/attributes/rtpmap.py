#!/usr/bin/env python

from value import AttributeValue
from error import ParseError
import re


class RtpmapValue(AttributeValue):
    """
    RFC 2327    SDP: Session Description Protocol
    a=rtpmap:<payload type> <encoding name>/<clock rate>[/<encoding parameters>]
    """

    attribute_name = "rtpmap"

    def __init__(self, payload_type, encoding_name, clock_rate, channels=None):
        assert type(payload_type) is int
        assert type(encoding_name) is str
        assert type(clock_rate) is int
        assert channels is None or type(channels) is int
        self.__payload_type = payload_type
        self.__encoding_name = encoding_name
        self.__clock_rate = clock_rate
        self.__channels = channels

    def __str__(self):
        result = "{0} {1}/{2}".format(self.__payload_type, self.__encoding_name, self.__clock_rate)
        if self.__channels is not None:
            result += "/" + str(self.__channels)
        return result

    @classmethod
    def from_string(cls, string):
        """
        a=rtpmap:97 /0
        """
        assert type(string) is str
        g = re.match("^(\d+) ([\w\d\-]*)/(\d+)(?:/(\d+))?$", string)
        if not g:
            raise ParseError("Error parsing rtpmap value: " + repr(string))
        return cls(int(g.group(1)), g.group(2), int(g.group(3)), int(g.group(4)) if g.group(4) else None)

    @property
    def payload_type(self):
        return self.__payload_type

    @property
    def encoding_name(self):
        return self.__encoding_name

    @property
    def clock_rate(self):
        return self.__clock_rate

    @property
    def channels(self):
        return self.__channels


if __name__ == "__main__":
    import unittest

    class RtpmapAttributeTest(unittest.TestCase):
        def test_init(self):
            self.failUnlessRaises(AssertionError, RtpmapValue, "95", "TestCodec", 90000)
            self.failUnlessRaises(AssertionError, RtpmapValue, 96, "TestCodec", 90000, "2")
            self.failUnlessRaises(AssertionError, RtpmapValue, 97, "TestCodec", None)
            RtpmapValue(98, "TestCodec", 90000, 2)
            RtpmapValue(99, "TestCodec", 90000)

        def test_parse(self):
            rtpmap = RtpmapValue.from_string("96 H264/90000")
            self.failUnlessEqual(rtpmap.payload_type, 96)
            self.failUnlessEqual(rtpmap.encoding_name, "H264")
            self.failUnlessEqual(rtpmap.clock_rate, 90000)
            self.failUnless(rtpmap.channels is None)

            rtpmap = RtpmapValue.from_string("0 PCMA/24000/2")
            self.failUnlessEqual(rtpmap.payload_type, 0)
            self.failUnlessEqual(rtpmap.encoding_name, "PCMA")
            self.failUnlessEqual(rtpmap.clock_rate, 24000)
            self.failUnlessEqual(rtpmap.channels, 2)

            self.failUnlessRaises(AssertionError, RtpmapValue.from_string, None)
            self.failUnlessRaises(AssertionError, RtpmapValue.from_string, 0)
            self.failUnlessRaises(ParseError, RtpmapValue.from_string, "xxx")
            self.failUnlessRaises(ParseError, RtpmapValue.from_string, "0 PCMA/24000/2/3")

        def test_str(self):
            rtpmap = RtpmapValue.from_string("0 PCMA/24000/2")
            self.failUnless(str(rtpmap) == "0 PCMA/24000/2")

            rtpmap = RtpmapValue.from_string("96 H264/90000")
            self.failUnless(str(rtpmap) == "96 H264/90000")

            rtpmap = RtpmapValue(97, "VP9", 0, 0)
            self.failUnless(str(rtpmap) == "97 VP9/0/0")

    unittest.main()
