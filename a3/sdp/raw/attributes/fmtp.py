#!/usr/bin/env python
"""
a=fmtp:<format> <format specific parameters>
Ex:
    a=fmtp:96 0-16
    a=fmtp:18 annexb=no
    a=fmtp:96 mode=3;vbr=off
    a=fmtp:99 mode-set=7
    a=fmtp:98 profile-level-id=1;config=000001B001000001B5090000010000000120008440FA282C2090A21F
    a=fmtp:99 packetization-mode=0;profile-level-id=42e011;sprop-parameter-sets=Z0LgC5ZUCg/I,aM4BrFSAa
    a=fmtp:98 sampling=YCbCr-4:2:2; width=800; height=600; delivery-method=inline; configuration=somebase16string;

    a=fmtp:99 packetization-mode=1
    a=fmtp:102 QCIF=1;CIF=1
    a=fmtp:100 keyFrameInterval=100
    a=fmtp:9 bitrate=64000


    a=rtpmap:97 speex/16000
    a=fmtp:97 mode="10,any"
    a=fmtp:97 mode=4
"""


from value import AttributeValue
from error import ParseError
import re


class FmtpValue(AttributeValue):

    attribute_name = "fmtp"

    def __init__(self, format_, parameters):
        assert type(format_) is int
        assert type(parameters) is str
        self.__format = format_
        self.__parameters = parameters

    @property
    def payload_type(self):
        return self.__format

    @property
    def parameters(self):
        return self.__parameters

    def get_parameter(self, name):
        for p in self.__parameters.split(";"):
            g = re.match("^(.+)=(.+)$", p)
            if g and g.group(1) == name:
                return g.group(2)
        return None

    def __str__(self):
        return "%d %s" % (self.__format, self.__parameters)

    @classmethod
    def from_string(cls, string):
        assert type(string) is str
        g = re.match("^(\d+) (.+)$", string)
        if not g:
            raise ParseError("Error parsing fmtp value: " + repr(string))
        return cls(int(g.group(1)), g.group(2))


if __name__ == "__main__":
    import unittest

    class FmtpValueTest(unittest.TestCase):
        def test_init(self):
            FmtpValue(96, "0-16")
            FmtpValue(18, "annexb=no")
            FmtpValue(96, "mode=3;vbr=off")
            FmtpValue(99, "mode-set=7")
            FmtpValue(98, "profile-level-id=1;config=000001B001000001B5090000010000000120008440FA282C2090A21F")
            self.failUnlessRaises(AssertionError, FmtpValue, 100L, "mode-set=7")
            self.failUnlessRaises(AssertionError, FmtpValue, 100, None)

        def test_str(self):
            self.failUnlessEqual(str(FmtpValue(96, "0-16")), "96 0-16")
            self.failUnlessEqual(str(FmtpValue(18, "annexb=no")), "18 annexb=no")
            self.failUnlessEqual(str(FmtpValue(96, "mode=3;vbr=off")), "96 mode=3;vbr=off")
            self.failUnlessEqual(str(FmtpValue(99, "mode-set=7")), "99 mode-set=7")
            fmtp = FmtpValue(98, "profile-level-id=1;config=000001B001000001B5090000010000000120008440FA282C2090A21F")
            fmtp_str = "98 profile-level-id=1;config=000001B001000001B5090000010000000120008440FA282C2090A21F"
            self.failUnlessEqual(str(fmtp), fmtp_str)

        def test_parser(self):
            fmtp = FmtpValue.from_string("96 1-13;mode=3;vbr=off")
            self.failUnlessEqual(fmtp.payload_type, 96)
            self.failUnlessEqual(fmtp.parameters, "1-13;mode=3;vbr=off")
            self.failUnlessEqual(fmtp.get_parameter("mode"), "3")
            self.failUnlessEqual(fmtp.get_parameter("vbr"), "off")

    unittest.main()
