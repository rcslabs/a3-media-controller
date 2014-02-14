#!/usr/bin/env python
"""
    rfc6236
    a=imageattr:PT send attr-list recv attr-list
    a=imageattr:PT send attr-list recv *
    a=imageattr:PT recv attr-list
    ex:
    a=imageattr:97 send [x=800,y=640,sar=1.1,q=0.6] [x=480,y=320] \
                   recv [x=330,y=250]
    a=imageattr:97 recv [x=800,y=640,sar=1.1] \
                   send [x=330,y=250]
    a=imageattr:97 recv [x=800,y=640,sar=1.1] \
                   send [x=[320:16:640],y=[240:16:480],par=[1.2-1.3]]
    a=imageattr:97 send [x=[480:16:800],y=[320:16:640],par=[1.2-1.3],q=0.6] \
                        [x=[176:8:208],y=[144:8:176],par=[1.2-1.3]] \
                   recv *
    a=imageattr:99 send [x=176,y=144] [x=224,y=176] [x=272,y=224] [x=320,y=240] \
                   recv [x=176,y=144] [x=224,y=176] [x=272,y=224,q=0.6] [x=320,y=240]
    a=imageattr:99 send [x=320,y=240]
    a=imageattr:100 recv [x=320,y=240]
    a=imageattr:97 send [x=400:16:800],y=[320:16:640],sar=[1.0-1.3],par=[1.2-1.3]] \
                   recv [x=800,y=600,sar=1.1]
    a=imageattr:97 recv [x=464,y=384,sar=1.15] \
                   send [x=800,y=600,sar=1.1]

    TODO: add classes to parse value correctly http://tools.ietf.org/html/rfc6236#section-3.1.1
    KeyValue, xyrange,  AttrList
"""


from value import AttributeValue
from error import ParseError
import re


class ImageattrValue(AttributeValue):

    attribute_name = "imageattr"

    def __init__(self, pt, send=None, recv=None):
        assert type(pt) is int
        assert send is None or type(send) is str
        assert recv is None or type(recv) is str
        self.__pt = pt
        self.__send = send
        self.__recv = recv

    @property
    def payload_type(self):
        return self.__pt

    @property
    def send(self):
        return self.__send

    @property
    def recv(self):
        return self.__recv

    def __str__(self):
        result = str(self.__pt)
        if self.__send:
            result += " send " + str(self.__send)
        if self.__recv:
            result += " recv " + str(self.__recv)
        return result

    @classmethod
    def from_string(cls, string):
        assert type(string) is str
        g = re.match("^(\d+) send (.+)(?: recv (.+))?$", string)
        if g:
            return cls(int(g.group(1)), g.group(2), g.group(3))
        else:
            g = re.match("^(\d+) recv (.+)(?: send (.+))?$", string)
            if g:
                return cls(int(g.group(1)), g.group(3), g.group(2))
            else:
                raise ParseError("Error parsing imageattr value: " + repr(string))


if __name__ == "__main__":
    import unittest

    class ImageattrValuetest(unittest.TestCase):
        def test_init(self):
            ImageattrValue(97, "[x=800,y=640,sar=1.1,q=0.6] [x=480,y=320]")
            ImageattrValue(100, recv="[x=320,y=240]")

        def test_str(self):
            self.failUnlessEqual(str(ImageattrValue(97,
                                                    send="[x=800,y=640,sar=1.1,q=0.6] [x=480,y=320]",
                                                    recv="[x=330,y=250]")),
                                 "97 send [x=800,y=640,sar=1.1,q=0.6] [x=480,y=320] recv [x=330,y=250]")

        def test_parse(self):
            s1 = "97 send [x=800,y=640,sar=1.1,q=0.6] [x=480,y=320] recv [x=330,y=250]"
            s2 = "97 recv [x=800,y=640,sar=1.1] send [x=330,y=250]"
            s3 = "97 recv [x=800,y=640,sar=1.1] send [x=[320:16:640],y=[240:16:480],par=[1.2-1.3]]"
            s4 = "97 send [x=[480:16:800],y=[320:16:640],par=[1.2-1.3],q=0.6] " + \
                 "[x=[176:8:208],y=[144:8:176],par=[1.2-1.3]] recv *"
            s5 = "99 send [x=320,y=240]"
            s6 = "100 recv [x=320,y=240]"
            i1 = ImageattrValue.from_string(s1)
            i2 = ImageattrValue.from_string(s2)
            i3 = ImageattrValue.from_string(s3)
            i4 = ImageattrValue.from_string(s4)
            i5 = ImageattrValue.from_string(s5)
            i6 = ImageattrValue.from_string(s6)
            self.failUnlessEqual(str(i1), s1)
            self.failUnlessEqual(str(i2), s2)
            self.failUnlessEqual(str(i3), s3)
            self.failUnlessEqual(str(i4), s4)
            self.failUnlessEqual(str(i5), s5)
            self.failUnlessEqual(str(i6), s6)
            self.failUnlessEqual(i1.payload_type, 97)
            self.failUnlessEqual(i2.payload_type, 97)
            self.failUnlessEqual(i3.payload_type, 97)
            self.failUnlessEqual(i4.payload_type, 97)
            self.failUnlessEqual(i5.payload_type, 99)
            self.failUnlessEqual(i6.payload_type, 100)

    unittest.main()