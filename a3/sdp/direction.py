#!/usr/bin/env python


from raw.attribute import AttributeCollection, Attribute, SendRecvValue, RecvOnlyValue, SendOnlyValue, InactiveValue
from error import SemanticError


class _SdpDirectionValue(str):
    pass


class SdpDirection:
    SEND_RECV = _SdpDirectionValue("sendrecv")
    RECV_ONLY = _SdpDirectionValue("recvonly")
    SEND_ONLY = _SdpDirectionValue("sendonly")
    INACTIVE = _SdpDirectionValue("inactive")


class Direction(object):
    def __init__(self, attributes):
        assert type(attributes) is AttributeCollection
        self.__attributes = attributes
        directions = self.__attributes.get(("recvonly", "sendrecv", "inactive", "sendonly"))
        if len(directions) > 1:
            raise SemanticError("More than one direction attribute")
        self.__attribute = directions[0] if len(directions) == 1 else None

    @property
    def value(self):
        if self.__attribute:
            if self.__attribute.name == SdpDirection.SEND_RECV:
                return SdpDirection.SEND_RECV
            elif self.__attribute.name == SdpDirection.RECV_ONLY:
                return SdpDirection.SEND_ONLY
            elif self.__attribute.name == SdpDirection.SEND_ONLY:
                return SdpDirection.SEND_ONLY
            elif self.__attribute.name == SdpDirection.INACTIVE:
                return SdpDirection.INACTIVE
        else:
            return SdpDirection.SEND_RECV

    @value.setter
    def value(self, direction):
        assert type(direction) is _SdpDirectionValue
        new_attribute = None
        if direction == SdpDirection.SEND_RECV:
            new_attribute = Attribute("sendrecv", SendRecvValue())
        elif direction == SdpDirection.RECV_ONLY:
            new_attribute = Attribute("recvonly", RecvOnlyValue())
        elif direction == SdpDirection.SEND_ONLY:
            new_attribute = Attribute("sendonly", SendOnlyValue())
        elif direction == SdpDirection.INACTIVE:
            new_attribute = Attribute("inactive", InactiveValue())

        assert new_attribute is not None

        if self.__attribute:
            self.__attribute.after(new_attribute)
            self.__attribute.remove()
            self.__attribute = new_attribute
        else:
            self.__attributes.append(new_attribute)
            self.__attribute = new_attribute


if __name__ == "__main__":
    import unittest
    from raw.attribute import FmtpValue, PtimeValue

    def get_attrs():
        return dict(
            sendrecv=Attribute("sendrecv", SendRecvValue()),
            recvonly=Attribute("recvonly", RecvOnlyValue()),
            sendonly=Attribute("sendonly", SendOnlyValue()),
            inactive=Attribute("inactive", InactiveValue())
        )

    class DirectionTest(unittest.TestCase):
        def test_init(self):
            attributes = AttributeCollection()
            direction = Direction(attributes)
            self.failUnlessEqual(direction.value, SdpDirection.SEND_RECV)
            self.failUnlessEqual(len(attributes), 0)

            a = get_attrs()
            self.failUnlessRaises(SemanticError, Direction, AttributeCollection([a["sendrecv"], a["sendonly"]]))
            self.failUnlessRaises(SemanticError, Direction, AttributeCollection([a["sendrecv"], a["sendrecv"]]))
            attr0 = Attribute("fmtp", FmtpValue(99, "0-15"))
            attr2 = Attribute("ptime", PtimeValue(20))
            attributes = AttributeCollection([attr0, a["sendonly"], attr2])
            direction = Direction(attributes)
            self.failUnlessEqual(direction.value, SdpDirection.SEND_ONLY)
            direction.value = SdpDirection.INACTIVE
            self.failUnlessEqual(direction.value, SdpDirection.INACTIVE)
            self.failUnlessEqual(attributes[0], attr0)
            self.failUnlessEqual(attributes[2], attr2)

        def test_assign(self):
            attributes = AttributeCollection()
            direction = Direction(attributes)
            self.failUnlessEqual(direction.value, SdpDirection.SEND_RECV)
            self.failUnlessEqual(len(attributes), 0)

            direction.value = SdpDirection.SEND_ONLY
            self.failUnlessEqual(direction.value, SdpDirection.SEND_ONLY)
            self.failUnlessEqual(len(attributes), 1)

            direction.value = SdpDirection.SEND_RECV
            self.failUnlessEqual(direction.value, SdpDirection.SEND_RECV)
            self.failUnlessEqual(len(attributes), 1)

            direction.value = SdpDirection.INACTIVE
            self.failUnlessEqual(direction.value, SdpDirection.INACTIVE)
            self.failUnlessEqual(len(attributes), 1)

    unittest.main()
