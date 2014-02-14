#!/usr/bin/env python
"""
rfc5576
    a=ssrc:<ssrc-id> <attribute>
    a=ssrc:<ssrc-id> <attribute>:<value>
"""


from value import AttributeValue
from error import ParseError
import re


class SsrcValue(AttributeValue):

    attribute_name = "ssrc"

    def __init__(self, ssrc_id, attribute, value=None):
        assert type(ssrc_id) is long
        assert type(attribute) is str
        assert value is None or type(value) is str
        self.__ssrc_id, self.__attribute, self.__value = ssrc_id, attribute, value

    def __str__(self):
        return str(self.__ssrc_id) + " " + self.__attribute + ((":" + self.__value) if self.__value is not None else "")

    @classmethod
    def from_string(cls, string):
        assert type(string) is str
        g = re.match("^(\d+) ([\w\d\-]+?)(?::(.+))?$", string)
        if not g:
            raise ParseError("Error parsing ssrc value: " + repr(string))
        return cls(long(g.group(1)), g.group(2), g.group(3))

    @property
    def ssrc_id(self):
        return self.__ssrc_id

    @property
    def attribute(self):
        return self.__attribute

    @property
    def value(self):
        return self.__value


if __name__ == "__main__":
    import unittest

    class SsrcTest(unittest.TestCase):
        def test_init(self):
            self.failUnlessRaises(AssertionError, SsrcValue, 12, "cname")
            self.failUnlessRaises(AssertionError, SsrcValue, 12, None)
            SsrcValue(12L, "cname")
            SsrcValue(12L, "cname", "xxx")

        def test_str(self):
            self.failUnlessEqual(str(SsrcValue(1376842571L, "cname", "3/5vbaJ5YVHkUCBa")),
                                 "1376842571 cname:3/5vbaJ5YVHkUCBa")
            self.failUnlessEqual(
                str(SsrcValue(1376842571L, "msid", "pfReJyNmk521WnjwyTaKbzEMvrh2EuaLReXC a0")),
                "1376842571 msid:pfReJyNmk521WnjwyTaKbzEMvrh2EuaLReXC a0")
            self.failUnlessEqual(str(SsrcValue(699367371L, "mslabel", "QtJSHijcG65nXiTX8LuK8QxabfX4AMtLEFPA")),
                                 "699367371 mslabel:QtJSHijcG65nXiTX8LuK8QxabfX4AMtLEFPA")

        def test_parse(self):
            ssrc_value = SsrcValue.from_string("1376842571 cname:3/5vbaJ5YVHkUCBa")
            self.failUnlessEqual(ssrc_value.ssrc_id, 1376842571L)
            self.failUnlessEqual(ssrc_value.attribute, "cname")
            self.failUnlessEqual(ssrc_value.value, "3/5vbaJ5YVHkUCBa")

            ssrc_value = SsrcValue.from_string("1376842571 cname")
            self.failUnlessEqual(ssrc_value.ssrc_id, 1376842571L)
            self.failUnlessEqual(ssrc_value.attribute, "cname")
            self.failUnlessEqual(ssrc_value.value, None)

    unittest.main()
