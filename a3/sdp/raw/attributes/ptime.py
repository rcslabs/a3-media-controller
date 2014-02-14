#!/usr/bin/env python
"""
RFC 2327    SDP: Session Description Protocol
    a=ptime:<packet time>
"""


from value import AttributeValue
from error import ParseError
import re


class PtimeValue(AttributeValue):

    attribute_name = "ptime"

    def __init__(self, packet_time):
        assert type(packet_time) is int
        self.__packet_time = packet_time

    @property
    def packet_time(self):
        return self.__packet_time

    @packet_time.setter
    def packet_time(self, packet_time):
        assert type(packet_time) is int
        self.__packet_time = packet_time

    def __str__(self):
        return str(self.__packet_time)

    @classmethod
    def from_string(cls, string):
        assert type(string) is str
        g = re.match("^(\d+)$", string)
        if not g:
            raise ParseError("Error parsing ptime value: " + repr(string))
        return cls(int(g.group(1)))


if __name__ == "__main__":
    import unittest

    class PtimeTest(unittest.TestCase):
        def test_init(self):
            self.failUnlessRaises(AssertionError, PtimeValue, "30")
            self.failUnlessRaises(AssertionError, PtimeValue, None)
            PtimeValue(20)

        def test_parse(self):
            self.failUnless(PtimeValue.from_string("30").packet_time == 30)
            self.failUnlessRaises(AssertionError, PtimeValue.from_string, None)
            self.failUnlessRaises(AssertionError, PtimeValue.from_string, 20)
            self.failUnlessRaises(ParseError, PtimeValue.from_string, "xxx")
            self.failUnlessRaises(ParseError, PtimeValue.from_string, "0 PCMA/24000/2/3")

        def test_str(self):
            self.failUnless(str(PtimeValue.from_string("20")) == "20")
            self.failUnless(str(PtimeValue(30)) == "30")

    unittest.main()
