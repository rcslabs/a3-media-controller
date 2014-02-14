#!/usr/bin/env python


from raw.attribute import Attribute, AttributeCollection, RtcpMux as RtcpMuxAttribute, Rtcp as RtcpAttribute, \
    NetType, AddrType


class Rtcp(object):
    """
    RFC 3605 (http://www.rfc-editor.org/rfc/rfc3605.txt)
    Real Time Control Protocol (RTCP) attribute in Session Description Protocol (SDP)
    """

    def __init__(self, attributes):
        assert type(attributes) is AttributeCollection
        self.__attributes = attributes
        rtcps = attributes.get("rtcp")
        assert len(rtcps) < 2
        self.__rtcp_attribute = rtcps[0] if len(rtcps) == 1 else None

    def __nonzero__(self):
        return self.__rtcp_attribute is not None

    @property
    def port(self):
        return self.__rtcp_attribute.value.port if self.__rtcp_attribute else None

    @port.setter
    def port(self, port):
        assert type(port) is int
        if self.__rtcp_attribute is not None:
            self.__rtcp_attribute.value.port = port
        else:
            self.__add_attribute(port)

    @property
    def connection_address(self):
        return self.__rtcp_attribute.value.connection_address if self.__rtcp_attribute else None

    @connection_address.setter
    def connection_address(self, connection_address):
        assert type(connection_address) is str
        if self.__rtcp_attribute is not None:
            self.__rtcp_attribute.value.connection_address = connection_address
        else:
            self.__add_attribute(0, NetType.IN, AddrType.IP4, connection_address)

    def __add_attribute(self, port, nettype=None, addrtype=None, connection_address=None):
        assert self.__rtcp_attribute is None
        assert type(port) is int
        self.__rtcp_attribute = Attribute("rtcp", RtcpAttribute(port, nettype, addrtype, connection_address))
        self.__attributes.append(self.__rtcp_attribute)

    def __remove_attribute(self):
        assert self.__rtcp_attribute is not None
        self.__rtcp_attribute.remove()
        self.__rtcp_attribute = None


class RtcpMux(object):
    """
    RFC 5761
    Multiplexing RTP Data and Control Packets on a Single Port
    """

    def __init__(self, attributes):
        assert type(attributes) is AttributeCollection
        self.__attributes = attributes
        rtcpmuxs = attributes.get("rtcp-mux")
        assert len(rtcpmuxs) < 2
        self.__rtcpmux_attribute = rtcpmuxs[0] if len(rtcpmuxs) == 1 else None

    def __nonzero__(self):
        return self.value

    @property
    def value(self):
        return self.__rtcpmux_attribute is not None

    @value.setter
    def value(self, value):
        assert type(value) is bool
        if self.__rtcpmux_attribute is None and value:
            self.__add_attribute()
        elif self.__rtcpmux_attribute is not None and not value:
            self.__remove_attribute()

    def __add_attribute(self):
        assert self.__rtcpmux_attribute is None
        self.__rtcpmux_attribute = Attribute("rtcp-mux", RtcpMuxAttribute())
        self.__attributes.append(self.__rtcpmux_attribute)

    def __remove_attribute(self):
        assert self.__rtcpmux_attribute is not None
        self.__rtcpmux_attribute.remove()
        self.__rtcpmux_attribute = None


if __name__ == "__main__":
    import unittest
    from raw.attribute import RtpmapValue, FmtpValue

    ATTRIBUTES = [
        "ice-ufrag:username",
        "ice-pwd:password"
    ]

    class RtcpMuxTest(unittest.TestCase):
        def test_init(self):
            rtpmap96 = Attribute("rtpmap", RtpmapValue(96, "VP8", 90000, 1))
            fmtp96 = Attribute("fmtp", FmtpValue(96, "0-16"))
            rtcp_mux_attr = Attribute("rtcp-mux", RtcpMuxAttribute())

            attributes = AttributeCollection([rtpmap96, fmtp96, rtcp_mux_attr])
            rtcp_mux = RtcpMux(attributes)
            self.failUnlessEqual(rtcp_mux.value, True)

            attributes = AttributeCollection([rtpmap96, fmtp96])
            rtcp_mux = RtcpMux(attributes)
            self.failUnlessEqual(rtcp_mux.value, False)

        def test_modify(self):
            rtpmap96 = Attribute("rtpmap", RtpmapValue(96, "VP8", 90000, 1))
            fmtp96 = Attribute("fmtp", FmtpValue(96, "0-16"))
            rtcp_mux_attr = Attribute("rtcp-mux", RtcpMuxAttribute())

            attributes = AttributeCollection([rtpmap96, rtcp_mux_attr, fmtp96])
            rtcp_mux = RtcpMux(attributes)

            rtcp_mux.value = False
            self.failUnlessEqual(rtcp_mux.value, False)
            self.failUnlessEqual(list(attributes), [rtpmap96, fmtp96])

            rtcp_mux.value = True
            self.failUnlessEqual(rtcp_mux.value, True)
            self.failUnlessEqual(type(attributes[2].value), RtcpMuxAttribute)

    class RtcpTest(unittest.TestCase):
        def test_init(self):
            attributes = AttributeCollection([Attribute("rtpmap", RtpmapValue(96, "VP8", 90000, 1)),
                                              Attribute("fmtp", FmtpValue(96, "0-16")),
                                              Attribute("rtcp", RtcpAttribute(9999))])
            rtcp = Rtcp(attributes)
            self.failUnless(bool(rtcp))
            self.failUnlessEqual(rtcp.port, 9999)
            self.failUnlessEqual(rtcp.connection_address, None)

            attributes = AttributeCollection([Attribute("rtpmap", RtpmapValue(96, "VP8", 90000, 1)),
                                              Attribute("fmtp", FmtpValue(96, "0-16")),
                                              Attribute("rtcp",
                                                        RtcpAttribute(9999, NetType.IN, AddrType.IP4, "127.0.0.1"))])
            rtcp = Rtcp(attributes)
            self.failUnless(bool(rtcp))
            self.failUnlessEqual(rtcp.port, 9999)
            self.failUnlessEqual(rtcp.connection_address, "127.0.0.1")

            attributes = AttributeCollection([])
            rtcp = Rtcp(attributes)
            self.failIf(bool(rtcp))
            self.failUnlessEqual(rtcp.port, None)
            self.failUnlessEqual(rtcp.connection_address, None)

        def test_modify(self):
            attributes = AttributeCollection([Attribute("rtpmap", RtpmapValue(96, "VP8", 90000, 1)),
                                              Attribute("fmtp", FmtpValue(96, "0-16"))])
            rtcp = Rtcp(attributes)
            self.failIf(bool(rtcp))
            self.failUnlessEqual(rtcp.port, None)
            self.failUnlessEqual(rtcp.connection_address, None)
            rtcp.port = 9999
            self.failUnless(bool(rtcp))
            self.failUnlessEqual(rtcp.port, 9999)
            self.failUnlessEqual(rtcp.connection_address, None)
            self.failUnlessEqual(str(attributes[2]), "rtcp:9999")
            rtcp.connection_address = "127.0.0.1"
            self.failUnlessEqual(str(attributes[2]), "rtcp:9999 IN IP4 127.0.0.1")





    unittest.main()