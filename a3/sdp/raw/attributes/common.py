#!/usr/bin/env python


from error import ParseError


class NetTypeValue(str):
    pass


class NetType:
    IN = NetTypeValue("IN")

    @classmethod
    def from_string(cls, string):
        assert type(string) is str
        if string == "IN":
            return cls.IN
        else:
            raise ParseError("sdp::NetType is " + repr(string))


class AddrTypeValue(str):
    pass


class AddrType:
    IP4 = AddrTypeValue("IP4")
    IP6 = AddrTypeValue("IP6")

    @classmethod
    def from_string(cls, string):
        assert type(string) is str
        if string == "IP4":
            return cls.IP4
        elif string == "IP6":
            return cls.IP6
        else:
            raise ParseError("sdp::AddrType is " + repr(string))


if __name__ == "__main__":
    import unittest

    class NettypeAddrtypeTest(unittest.TestCase):
        def test_init(self):
            pass

        def test_str(self):
            self.failUnlessEqual(str(NetType.IN),   "IN")
            self.failUnlessEqual(str(AddrType.IP4), "IP4")
            self.failUnlessEqual(str(AddrType.IP6), "IP6")

        def test_parse(self):
            self.failUnlessEqual(NetType.from_string("IN"),   NetType.IN)
            self.failUnlessEqual(AddrType.from_string("IP4"), AddrType.IP4)
            self.failUnlessEqual(AddrType.from_string("IP6"), AddrType.IP6)

    unittest.main()
