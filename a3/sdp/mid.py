#!/usr/bin/env python


from raw.attribute import Attribute, AttributeCollection, StrAttributeValue
from raw.attribute import Mid as RawMid
from error import SemanticError


class Mid(object):
    def __init__(self, attributes):
        assert type(attributes) is AttributeCollection
        self.__attributes = attributes
        mids = self.__attributes.get("mid")
        if len(mids) > 1:
            raise SemanticError("More than one mid attribute")
        self.__attribute = mids[0] if len(mids) == 1 else None

    @property
    def value(self):
        return self.__attribute.value.value if self.__attribute else None

    @value.setter
    def value(self, value):
        assert value is None or type(value) is str
        if value is not None:
            self.__set_attribute(value)
        else:
            self.__remove_attribute()

    def __nonzero__(self):
        return self.value is not None

    def __set_attribute(self, value):
        assert type(value) is str
        if self.__attribute is None:
            self.__attribute = Attribute("mid", RawMid(value))
            self.__attribute.appendTo(self.__attributes)
        else:
            self.__attribute.value.value = value

    def __remove_attribute(self):
        if self.__attribute is not None:
            self.__attribute.remove()
            self.__attribute = None


if __name__ == "__main__":
    import unittest

    class MidTest(unittest.TestCase):
        def test_init_0(self):
            attributes = AttributeCollection()
            mid = Mid(attributes)
            self.failUnlessEqual(len(attributes), 0)
            self.failUnlessEqual(mid.value, None)
            self.failUnlessEqual(bool(mid), False)
            mid.value = None
            self.failUnlessEqual(len(attributes), 0)
            self.failUnlessEqual(mid.value, None)
            self.failUnlessEqual(bool(mid), False)
            mid.value = "mid-value"
            self.failUnlessEqual(len(attributes), 1)
            self.failUnlessEqual(str(attributes), "a=mid:mid-value\r\n")
            self.failUnlessEqual(mid.value, "mid-value")
            self.failUnlessEqual(bool(mid), True)

        def test_init_1(self):
            attributes = AttributeCollection([Attribute("mid", RawMid("mid-value"))])
            mid = Mid(attributes)
            self.failUnlessEqual(len(attributes), 1)
            self.failUnlessEqual(str(attributes), "a=mid:mid-value\r\n")
            self.failUnlessEqual(mid.value, "mid-value")
            self.failUnlessEqual(bool(mid), True)
            mid.value = None
            self.failUnlessEqual(len(attributes), 0)
            self.failUnlessEqual(str(attributes), "\r\n")
            self.failUnlessEqual(mid.value, None)
            self.failUnlessEqual(bool(mid), False)


    unittest.main()