#!/usr/bin/env python


from value import FlagAttributeValue, AttributeValue
from common import *

import re


class RtcpMux(FlagAttributeValue):
    attribute_name = "rtcp-mux"


#class RtcpFbValue(AttributeValue):
#    """
#    rfc4585
#    rtcp-fb-pt SP rtcp-fb-val CRLF
#    ex: a=rtcp-fb:96 nack
#        a=rtcp-fb:* nack
#        a=rtcp-fb:98 nack rpsi
#    """
#
#

class Rtcp(AttributeValue):
    """
    RFC 3605 (http://www.rfc-editor.org/rfc/rfc3605.txt)
      Real Time Control Protocol (RTCP) attribute in
                  Session Description Protocol (SDP)
    rtcp-attribute =  "a=rtcp:" port  [nettype-space addrtype-space connection-address] CRLF
    """
    attribute_name = "rtcp"

    def __init__(self, port, nettype=None, addrtype=None, connection_address=None):
        assert type(port) is int
        assert nettype is None or type(nettype) is NetTypeValue
        assert addrtype is None or type(addrtype) is AddrTypeValue
        assert connection_address is None or type(connection_address) is str
        self.__port = port
        self.__nettype = nettype
        self.__addrtype = addrtype
        self.__connection_address = connection_address

    @property
    def port(self):
        return self.__port

    @port.setter
    def port(self, port):
        assert type(port) is int
        self.__port = port

    @property
    def nettype(self):
        return self.__nettype

    @property
    def addrtype(self):
        return self.__addrtype

    @property
    def connection_address(self):
        return self.__connection_address

    @connection_address.setter
    def connection_address(self, connection_address):
        assert connection_address is None or type(connection_address) is str
        self.__nettype = NetType.IN
        self.__addrtype = AddrType.IP4
        self.__connection_address = connection_address

    def __str__(self):
        if self.__nettype and self.__addrtype and self.__connection_address:
            return "%d %s %s %s" % (self.__port, self.__nettype, self.__addrtype, self.__connection_address)
        else:
            return str(self.__port)

    @classmethod
    def from_string(cls, string):
        assert type(string) is str
        g = re.match("^(\d+)(?: (\w+) (\w+) (\S+))?$", string)
        if not g:
            raise ParseError("Error parsing rtcp value: " + repr(string))
        if g.group(2) and g.group(3) and g.group(4):
            return cls(int(g.group(1)),
                       NetType.from_string(g.group(2)),
                       AddrType.from_string(g.group(3)),
                       g.group(4))
        else:
            return cls(int(g.group(1)))


if __name__ == "__main__":
    import unittest

    class RtcpMuxTest(unittest.TestCase):
        def test_init(self):
            RtcpMux()

    class RtcpTest(unittest.TestCase):
        def test_init(self):
            self.failUnlessRaises(AssertionError, Rtcp, 1L)
            self.failUnlessRaises(AssertionError, Rtcp, 1, "Error", "Error", "Error")
            a = Rtcp(10, NetType.IN, AddrType.IP4, "127.0.0.1")
            self.failUnlessEqual(a.port, 10)
            self.failUnlessEqual(a.nettype, NetType.IN)
            self.failUnlessEqual(a.addrtype, AddrType.IP4)
            self.failUnlessEqual(a.connection_address, "127.0.0.1")

        def test_parse(self):
            a = Rtcp.from_string("53020")
            self.failUnlessEqual(a.port, 53020)
            self.failUnlessEqual(a.nettype, None)
            self.failUnlessEqual(a.addrtype, None)
            self.failUnlessEqual(a.connection_address, None)
            a = Rtcp.from_string("53020 IN IP4 126.16.64.4")
            self.failUnlessEqual(a.port, 53020)
            self.failUnlessEqual(a.nettype, NetType.IN)
            self.failUnlessEqual(a.addrtype, AddrType.IP4)
            self.failUnlessEqual(a.connection_address, "126.16.64.4")
            a = Rtcp.from_string("53020 IN IP6 2001:2345:6789:ABCD:EF01:2345:6789:ABCD")
            self.failUnlessEqual(a.port, 53020)
            self.failUnlessEqual(a.nettype, NetType.IN)
            self.failUnlessEqual(a.addrtype, AddrType.IP6)
            self.failUnlessEqual(a.connection_address, "2001:2345:6789:ABCD:EF01:2345:6789:ABCD")

        def test_str(self):
            self.failUnlessEqual(str(Rtcp.from_string("53020")), "53020")
            self.failUnlessEqual(str(Rtcp.from_string("53020 IN IP4 126.16.64.4")), "53020 IN IP4 126.16.64.4")
            self.failUnlessEqual(str(Rtcp.from_string("53020 IN IP6 2001:2345:6789:ABCD:EF01:2345:6789:ABCD")),
                                 "53020 IN IP6 2001:2345:6789:ABCD:EF01:2345:6789:ABCD")



    unittest.main()
