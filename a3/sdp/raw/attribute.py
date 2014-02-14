#!/usr/bin/env python


import re
from attributes.error import ParseError
from attributes.value import AttributeValue, FlagAttributeValue, StrAttributeValue
from attributes.direction import *
from attributes.rtpmap import RtpmapValue
from attributes.imageattr import ImageattrValue
from attributes.ice import *
from attributes.crypto import *
from attributes.ptime import PtimeValue
from attributes.fmtp import FmtpValue
from attributes.ssrc import SsrcValue
from attributes.silence_supp import *
from attributes.rtcp import *
from attributes.group import *
from attributes.mid import *


ATTRIBUTE_MAP = {
    "rtpmap":       RtpmapValue,
    "ptime":        PtimeValue,
    "crypto":       CryptoValue,
    "sendrecv":     SendRecvValue,
    "sendonly":     SendOnlyValue,
    "recvonly":     RecvOnlyValue,
    "inactive":     InactiveValue,
    "fmtp":         FmtpValue,
    "imageattr":    ImageattrValue,
    "ssrc":         SsrcValue,
    "ice-ufrag":    IceUfragValue,
    "ice-pwd":      IcePwdValue,
    "ice-options":  IceOptionsValue,
    "ice-lite":     IceLiteValue,
    "ice-mismatch": IceMismatchValue,
    "silenceSupp":  SilenceSuppValue,
    "rtcp-mux":     RtcpMux,
    "rtcp":         Rtcp,
    "group":        Group,
    "mid":          Mid,
    "":             StrAttributeValue
}


##m=audio 9999 RTP/AVP 96
##a=rtpmap:96 speex/16000
##a=ptime:40
##a=fmtp:96 vbr=on;cng=on
##
##  <payload-type id='96' name='speex' clockrate='16000' ptime='40'>
##    <parameter name='vbr' value='on'/>
##    <parameter name='cng' value='on'/>
##  </payload-type>
##
##
##m=video 49170 RTP/AVP 98
##a=rtpmap:98 theora/90000
##
##
##<description xmlns='urn:xmpp:jingle:apps:rtp:1' media='video'>
##  <payload-type id='98' name='theora' clockrate='90000'>
##    <parameter name='height' value='600'/>
##    <parameter name='width' value='800'/>
##    <parameter name='delivery-method' value='inline'/>
##    <parameter name='configuration' value='somebase16string'/>
##    <parameter name='sampling' value='YCbCr-4:2:2'/>
##  </payload-type>
##</description>
#
#
#
#
#draft-alvestrand-mmusic-msid-02
#   http://tools.ietf.org/html/draft-alvestrand-mmusic-msid-02#section-2
#
#     ; "attribute" is defined in RFC 4566.
#     ; This attribute should be used with the ssrc-attr from RFC 5576.
#     attribute =/ msid-attr
#     msid-attr = "msid:" identifier [ " " appdata ]
#     identifier = token
#     appdata = token
#
#
#   An example MSID value for the SSRC 1234 might look like this:
#     a=ssrc:1234 msid:examplefoo v1
#


class Attribute(object):
    """
    5.13.  Attributes ("a=")
    a=<attribute>
    a=<attribute>:<value>
    """
    def __init__(self, name, value, collection=None):
        assert type(name) is str
        assert isinstance(value, AttributeValue)
        assert collection is None or type(collection) is AttributeCollection
        if name in ATTRIBUTE_MAP:
            assert type(value) is ATTRIBUTE_MAP[name]
        self.__name = name
        self.__value = value
        self.__collection = None
        self.appendTo(collection)

    def __str__(self):
        if isinstance(self.__value, FlagAttributeValue):
            return self.__name
        else:
            return "%s:%s" % (self.__name, self.__value)

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        assert type(name) is str
        self.__name = name

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        assert isinstance(value, AttributeValue)
        self.__value = value

    @property
    def collection(self):
        return self.__collection

    @collection.setter
    def collection(self, collection):
        assert collection is None or type(collection) is AttributeCollection
        self.appendTo(collection)

    def appendTo(self, collection):
        assert collection is None or type(collection) is AttributeCollection
        if self.__collection is collection:
            return
        self.remove()
        if collection is not None:
            self.__collection = collection
            self.__collection.append(self)

    def remove(self):
        if self.__collection is None:
            return
        collection = self.__collection
        self.__collection = None
        collection.remove(self)

    def insert_before(self, other):
        assert type(other) is Attribute
        other.before(self)

    def insert_after(self, other):
        assert type(other) is Attribute
        other.after(self)

    def after(self, other):
        assert type(other) is Attribute
        assert self.__collection
        self.__collection.insert_after(other, self)

    def before(self, other):
        assert type(other) is Attribute
        assert self.__collection
        self.__collection.insert_before(other, self)

    @classmethod
    def from_string(cls, string, collection=None):
        """
        Parse string in format <attribute>:<value>
        and creates value corresponding to attribute
        """
        assert type(string) is str
        assert collection is None or type(collection) is AttributeCollection
        g = re.match("^(.+?)(?::(.+))?$", string)
        if not g:
            raise ParseError("Error parsing sdp attribute " + repr(string))
        str_name, str_value = g.group(1), g.group(2)
        if str_name not in ATTRIBUTE_MAP:
            value = StrAttributeValue(str_value)
        else:
            value = ATTRIBUTE_MAP[str_name].from_string(str_value)
        return cls(str_name, value, collection)


class AttributeCollection(object):
    def __init__(self, attributes=None):
        self.__attributes = attributes or []
        for attribute in self.__attributes:
            assert type(attribute) is Attribute
            attribute.collection = self

    def __nonzero__(self):
        return len(self.__attributes) != 0

    def __bool__(self):
        return self.__nonzero__()

    def __len__(self):
        return len(self.__attributes)

    def __iter__(self):
        return self.__attributes.__iter__()

    def __contains__(self, item):
        assert type(item) is Attribute
        return item in self.__attributes

    def __getitem__(self, item):
        return self.__attributes[item]

    @property
    def first(self):
        return self.__attributes[0] if len(self.__attributes) else None

    @property
    def first_value(self):
        return self.__attributes[0].value if len(self.__attributes) else None

    def __index_of(self, item):
        assert type(item) is Attribute
        assert item in self.__attributes
        return self.__attributes.index(item)

    def insert_after(self, new_item, item):
        assert type(new_item) is Attribute and type(item) is Attribute
        if new_item is item:
            return
        i = self.__index_of(item)
        if new_item in self.__attributes:
            self.__attributes.remove(new_item)
        self.__attributes.insert(i+1, new_item)
        new_item.collection = self

    def insert_before(self, new_item, item):
        assert type(new_item) is Attribute and type(item) is Attribute
        if new_item in self.__attributes:
            return
        i = self.__index_of(item)
        self.__attributes.insert(i, new_item)
        new_item.collection = self

    def append(self, new_item):
        if new_item in self.__attributes:
            return
        self.__attributes.append(new_item)
        new_item.collection = self

    def prepend(self, new_item):
        if new_item in self.__attributes:
            return
        self.__attributes.insert(0, new_item)
        new_item.collection = self

    def insert_with_order(self, *args):
        if len(args) == 0:
            return
        first_existing = None
        for i in range(len(args)):
            if args[i] in self:
                first_existing = i
                break
        if first_existing is None:
            self.append(args[0])
            first_existing = 0
        for i in range(first_existing, 0, -1):
            args[i].before(args[i-1])
        for i in range(first_existing+1, len(args)):
            if args[i] not in self:
                args[i-1].after(args[i])

    def remove(self, attribute):
        assert type(attribute) is Attribute
        assert attribute in self.__attributes
        attribute.collection = None
        if attribute in self.__attributes:
            self.__attributes.remove(attribute)

    def get(self, *args):
        """
        returns attributes or list of attributes selected by names
        """
        assert len(args) >= 1
        result = []
        for arg in args:
            names = [arg] if isinstance(arg, str) else arg
            result.append(filter(lambda attr: attr.name in names, self.__attributes))

        return result[0] if len(result) == 1 else result

    def __call__(self, *args):
        return self.get(*args)

    def to_str_list(self):
        return ["a=" + str(attr) for attr in self.__attributes]

    def __str__(self):
        return '\r\n'.join(self.to_str_list()) + '\r\n'

    def __contains__(self, item):
        assert type(item) is Attribute
        return item in self.__attributes


if __name__ == "__main__":
    import unittest

    class AttributeTest(unittest.TestCase):
        def test_init(self):
            self.failUnlessRaises(AssertionError, Attribute, 0, 0)
            Attribute("inactive", InactiveValue(), None)
            self.failUnlessRaises(AssertionError, Attribute, "ptime", InactiveValue())

        def test_init2(self):
            collection1 = AttributeCollection()
            a_inactive = Attribute("inactive", InactiveValue(), collection1)
            self.failUnlessEqual(collection1.to_str_list(), ['a=inactive'])
            collection2 = AttributeCollection()
            a_inactive.appendTo(collection2)
            self.failUnlessEqual(collection1.to_str_list(), [])
            self.failUnlessEqual(collection2.to_str_list(), ['a=inactive'])
            a_inactive.remove()
            self.failUnlessEqual(collection1.to_str_list(), [])
            self.failUnlessEqual(collection2.to_str_list(), [])

        def test_insert(self):
            collection1 = AttributeCollection()
            inactive = Attribute("inactive", InactiveValue(), collection1)
            sendrecv = Attribute("sendrecv", SendRecvValue(), collection1)
            self.failUnlessEqual(collection1.to_str_list(), ['a=inactive', 'a=sendrecv'])
            rtpmap = Attribute("rtpmap", RtpmapValue(96, "VP8", 90000))
            inactive.after(rtpmap)
            self.failUnlessEqual(collection1.to_str_list(), ['a=inactive',
                                                             'a=rtpmap:96 VP8/90000',
                                                             'a=sendrecv'])
            collection1.remove(rtpmap)
            self.failUnlessEqual(collection1.to_str_list(), ['a=inactive', 'a=sendrecv'])
            sendrecv.before(rtpmap)
            self.failUnlessEqual(collection1.to_str_list(), ['a=inactive',
                                                             'a=rtpmap:96 VP8/90000',
                                                             'a=sendrecv'])
            rtpmap.after(rtpmap)
            self.failUnlessEqual(collection1.to_str_list(), ['a=inactive',
                                                             'a=rtpmap:96 VP8/90000',
                                                             'a=sendrecv'])
            inactive.insert_after(sendrecv)
            self.failUnlessEqual(collection1.to_str_list(), ['a=rtpmap:96 VP8/90000',
                                                             'a=sendrecv',
                                                             'a=inactive'])

        def test_insert_with_order(self):
            a1 = Attribute("sendrecv", SendRecvValue())
            a2 = Attribute("rtpmap", RtpmapValue(99, "TestCodec", 90000))
            a3 = Attribute("fmtp", FmtpValue(96, "0-16"))
            a4 = Attribute("imageattr", ImageattrValue(100, recv="[x=320,y=240]"))
            a5 = Attribute("ssrc", SsrcValue(12L, "cname", "xxx"))
            c = AttributeCollection([a1, a2])
            c.insert_with_order(a3, a4, a5)
            self.failUnlessEqual(list(c), [a1, a2, a3, a4, a5])
            c = AttributeCollection()
            c.insert_with_order(a1, a2, a3, a4, a5)
            self.failUnlessEqual(list(c), [a1, a2, a3, a4, a5])
            c = AttributeCollection([a4, a5])
            c.insert_with_order(a1, a2, a3, a4)
            self.failUnlessEqual(list(c), [a1, a2, a3, a4, a5])
            c = AttributeCollection([a2, a3, a4])
            c.insert_with_order(a1, a2, a4, a5)
            self.failUnlessEqual(list(c), [a1, a2, a3, a4, a5])

    unittest.main()
