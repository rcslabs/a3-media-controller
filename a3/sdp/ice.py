#!/usr/bin/env python
"""
rfc5245
Interactive Connectivity Establishment (ICE):
    A Protocol for Network Address Translator (NAT) Traversal for Offer/Answer Protocols
"""


import raw.attribute
import random


ICE_CHAR = "ABCDEFGHIJHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"


class Ice(object):
    def __init__(self, attributes):
        assert type(attributes) is raw.attribute.AttributeCollection
        self.__attributes = attributes
        ufrags, pwds, optionss, lites, mismatchs = attributes.get("ice-ufrag", "ice-pwd", "ice-options", "ice-lite",
                                                                  "ice-mismatch")
        assert (len(ufrags) < 2 and
                len(pwds) < 2 and
                len(optionss) < 2 and
                len(lites) < 2 and
                len(mismatchs) < 2)
        self.__ufrag_attribute = ufrags[0] if len(ufrags) == 1 else None
        self.__pwd_attribute = pwds[0] if len(pwds) == 1 else None
        self.__options_attribute = optionss[0] if len(optionss) == 1 else None
        self.__lite_attribute = lites[0] if len(lites) == 1 else None
        self.__mismatch_attribute = mismatchs[0] if len(mismatchs) == 1 else None

    def __insert_attributes(self):
        args = filter(lambda a: a is not None, [self.__lite_attribute,
                                                self.__ufrag_attribute,
                                                self.__pwd_attribute,
                                                self.__options_attribute,
                                                self.__mismatch_attribute])
        self.__attributes.insert_with_order(*args)

    @property
    def ufrag(self):
        return str(self.__ufrag_attribute.value) if self.__ufrag_attribute else None

    @ufrag.setter
    def ufrag(self, ufrag_value):
        assert ufrag_value is None or type(ufrag_value) is str
        if ufrag_value is not None:
            self.__set_ufrag_attribute(ufrag_value)
        else:
            self.__remove_ufrag_attribute()

    @property
    def pwd(self):
        return str(self.__pwd_attribute.value) if self.__pwd_attribute else None

    @pwd.setter
    def pwd(self, pwd_value):
        assert pwd_value is None or type(pwd_value) is str
        if pwd_value is not None:
            self.__set_pwd_attribute(pwd_value)
        else:
            self.__remove_pwd_attribute()

    @property
    def options(self):
        return str(self.__options_attribute) if self.__options_attribute else None

    @options.setter
    def options(self, options_value):
        assert options_value is None or type(options_value) is str
        if options_value is not None:
            self.__set_options_attribute(options_value)
        else:
            self.__remove_options_attribute()

    @property
    def lite(self):
        return bool(self.__lite_attribute)

    @property
    def mismatch(self):
        return bool(self.__mismatch_attribute)

    def __nonzero__(self):
        return bool(self.__ufrag_attribute or self.__lite_attribute)

    def generate_google_ice(self):
        """
        generate new ice options
        RFC 5245:
            ice-char        = ALPHA / DIGIT / "+" / "/"
            ufrag           = 4*256ice-char
            password        = 22*256ice-char
        """
        self.ufrag = "".join(random.choice(ICE_CHAR) for _ in range(16))
        self.pwd = "".join(random.choice(ICE_CHAR) for _ in range(24))
        self.options = "google-ice"

    def __set_ufrag_attribute(self, str_value):
        assert type(str_value) is str
        if self.__ufrag_attribute:
            self.__ufrag_attribute.value.value = str_value
        else:
            self.__ufrag_attribute = raw.attribute.Attribute("ice-ufrag", raw.attribute.IceUfragValue(str_value))
            self.__insert_attributes()

    def __remove_ufrag_attribute(self):
        if self.__ufrag_attribute is not None:
            self.__ufrag_attribute.remove()
            self.__ufrag_attribute = None

    def __set_pwd_attribute(self, str_value):
        assert type(str_value) is str
        if self.__pwd_attribute is not None:
            self.__pwd_attribute.value.value = str_value
        else:
            self.__pwd_attribute = raw.attribute.Attribute("ice-pwd", raw.attribute.IcePwdValue(str_value))
            self.__insert_attributes()

    def __remove_pwd_attribute(self):
        if self.__pwd_attribute is not None:
            self.__pwd_attribute.remove()
            self.__pwd_attribute = None

    def __set_options_attribute(self, str_value):
        assert type(str_value) is str
        if self.__options_attribute:
            self.__options_attribute.value.value = str_value
        else:
            self.__options_attribute = raw.attribute.Attribute("ice-options",
                                                               raw.attribute.IceOptionsValue(str_value))
            self.__insert_attributes()

    def __remove_options_attribute(self):
        if self.__options_attribute is not None:
            self.__options_attribute.remove()
            self.__options_attribute = None


if __name__ == "__main__":

    import unittest

    ATTRIBUTES = [
        "ice-ufrag:UFRAGUFRAGUFRAG",
        "ice-pwd:PWDPWDPWD"
    ]

    def get_attribute_collection():
        collection = raw.attribute.AttributeCollection()
        for s in ATTRIBUTES:
            collection.append(raw.attribute.Attribute.from_string(s))
        return collection

    class TestIce(unittest.TestCase):
        def test_init(self):
            ice = Ice(raw.attribute.AttributeCollection())
            if ice:
                self.fail("Ice is True")
            ice = Ice(get_attribute_collection())
            if not ice:
                self.fail("Ice is False")

        def test_modify(self):
            attributes = get_attribute_collection()
            ice = Ice(attributes)
            ice.pwd = "password"
            self.failUnlessEqual(str(attributes), "a=ice-ufrag:UFRAGUFRAGUFRAG\r\na=ice-pwd:password\r\n")
            ice.ufrag = "username"
            self.failUnlessEqual(str(attributes), "a=ice-ufrag:username\r\na=ice-pwd:password\r\n")
            ice.options = "google-ice"
            self.failUnlessEqual(str(attributes),
                                 "a=ice-ufrag:username\r\na=ice-pwd:password\r\na=ice-options:google-ice\r\n")
            ice.pwd = None
            self.failUnlessEqual(str(attributes), "a=ice-ufrag:username\r\na=ice-options:google-ice\r\n")
            ice.options = None
            self.failUnlessEqual(str(attributes), "a=ice-ufrag:username\r\n")


        def test_create(self):
            attributes = raw.attribute.AttributeCollection()
            ice = Ice(attributes)
            ice.pwd = "password"
            self.failUnlessEqual(str(attributes), "a=ice-pwd:password\r\n")
            ice.ufrag = "username"
            self.failUnlessEqual(str(attributes), "a=ice-ufrag:username\r\na=ice-pwd:password\r\n")

        def test_generate(self):
            ice = Ice(raw.attribute.AttributeCollection())
            if ice:
                self.fail("Ice is True")

    unittest.main()
