#!/usr/bin/env python
"""
RFC 3108
http://tools.ietf.org/html/rfc3108#page-63
a=silenceSupp: <silenceSuppEnable> <silenceTimer> <suppPref> <sidUse> <fxnslevel>

Ex:
    a=silenceSupp:off - - - -
    a=silenceSupp:on 250 standard Fixed Noise 30
"""


from value import AttributeValue
from error import ParseError
import re


class _SilenceSuppPrefValue(str):
    pass


class SilenceSuppPref:
    STANDARD = _SilenceSuppPrefValue("standard")
    CUSTOM = _SilenceSuppPrefValue("custom")

    @classmethod
    def from_string(cls, string):
        assert type(string) is str
        if string == cls.STANDARD:
            return cls.STANDARD
        elif string == cls.CUSTOM:
            return cls.CUSTOM
        elif string == "-":
            return None
        else:
            raise ParseError("SilenceSuppPref is " + repr(string))


class _SilenceSuppSidUseValue(str):
    pass


class SilenceSuppSidUse:

    attribute_name = "silenceSupp"

    NO_SID = "No SID"
    FIXED_NOISE = "Fixed Noise"
    SAMPLED_NOISE = "Sampled Noise"

    @classmethod
    def from_string(cls, string):
        assert type(string) is str
        if string == cls.NO_SID:
            return cls.NO_SID
        elif string == cls.FIXED_NOISE:
            return cls.FIXED_NOISE
        elif string == cls.SAMPLED_NOISE:
            return cls.SAMPLED_NOISE
        elif string == "-":
            return None
        else:
            raise ParseError("SilenceSuppSidUse is " + repr(string))


class SilenceSuppValue(AttributeValue):
    def __init__(self, silence_supp_enable=False, silence_timer=None, supp_pref=None, sid_use=None, fxnslevel=None):
        assert type(silence_supp_enable) is bool
        assert silence_timer is None or type(silence_timer) is int
        assert supp_pref is None or type(supp_pref) is _SilenceSuppPrefValue
        assert sid_use is None or type(sid_use is _SilenceSuppSidUseValue)
        assert fxnslevel is None or type(fxnslevel) is int
        self.__silence_supp_enable = silence_supp_enable
        self.__silence_timer = silence_timer
        self.__supp_pref = supp_pref
        self.__sid_use = sid_use
        self.__fxnslevel = fxnslevel

    @property
    def silence_supp_enable(self):
        return self.__silence_supp_enable

    @property
    def silence_timer(self):
        return self.__silence_timer

    @property
    def supp_pref(self):
        return self.__supp_pref

    @property
    def sid_use(self):
        return self.__sid_use

    @property
    def fxnslevel(self):
        return self.__fxnslevel

    def __str__(self):
        return "{0} {1} {2} {3} {4}".format("on" if self.__silence_supp_enable else "off",
                                            self.__silence_timer if self.__silence_timer is not None else "-",
                                            str(self.__supp_pref) if self.__supp_pref is not None else "-",
                                            str(self.__sid_use) if self.__sid_use is not None else "-",
                                            self.__fxnslevel if self.__fxnslevel is not None else "-")

    @classmethod
    def from_string(cls, string):
        assert type(string) is str
        g = re.match("^(on|off) (\-|\d+) (\-|standard|custom) (\-|No SID|Fixed Noise|Sampled Noise) (\-|\d+)$", string)
        if g:
            silence_supp_enable = True if g.group(1) == "on" else False
            silence_timer = int(g.group(2)) if g.group(2) != "-" else None
            supp_pref = SilenceSuppPref.from_string(g.group(3))
            sid_use = SilenceSuppSidUse.from_string(g.group(4))
            fxnslevel = int(g.group(5)) if g.group(5) != "-" else None
            return cls(silence_supp_enable, silence_timer, supp_pref, sid_use, fxnslevel)
        else:
            raise ParseError("Error parsing silenceSupp value: " + repr(string))


if __name__ == "__main__":
    import unittest

    class SilenceSuppValuetest(unittest.TestCase):
        def test_init(self):
            v = SilenceSuppValue()
            self.failUnlessEqual(v.silence_supp_enable, False)
            self.failUnlessEqual(v.silence_timer, None)
            self.failUnlessEqual(v.supp_pref, None)
            self.failUnlessEqual(v.sid_use, None)
            self.failUnlessEqual(v.fxnslevel, None)

            v = SilenceSuppValue(True, supp_pref=SilenceSuppPref.CUSTOM, sid_use=SilenceSuppSidUse.SAMPLED_NOISE)
            self.failUnlessEqual(v.silence_supp_enable, True)
            self.failUnlessEqual(v.silence_timer, None)
            self.failUnlessEqual(v.supp_pref, SilenceSuppPref.CUSTOM)
            self.failUnlessEqual(v.sid_use, SilenceSuppSidUse.SAMPLED_NOISE)
            self.failUnlessEqual(v.fxnslevel, None)

        def test_str(self):
            v = SilenceSuppValue(True, supp_pref=SilenceSuppPref.CUSTOM, sid_use=SilenceSuppSidUse.SAMPLED_NOISE)
            self.failUnlessEqual(str(v), "on - custom Sampled Noise -")
            v = SilenceSuppValue()
            self.failUnlessEqual(str(v), "off - - - -")
            v = SilenceSuppValue(True, 250, SilenceSuppPref.STANDARD, SilenceSuppSidUse.FIXED_NOISE, 30)
            self.failUnlessEqual(str(v), "on 250 standard Fixed Noise 30")

        def test_parse(self):
            self.failUnlessRaises(ParseError, SilenceSuppValue.from_string, "on -")
            self.failUnlessRaises(ParseError, SilenceSuppValue.from_string, "on 250 Fixed Noise standard 30")

            v = SilenceSuppValue.from_string("on 250 standard Fixed Noise 30")
            self.failUnlessEqual(v.silence_supp_enable, True)
            self.failUnlessEqual(v.silence_timer, 250)
            self.failUnlessEqual(v.supp_pref, SilenceSuppPref.STANDARD)
            self.failUnlessEqual(v.sid_use, SilenceSuppSidUse.FIXED_NOISE)
            self.failUnlessEqual(v.fxnslevel, 30)
            v = SilenceSuppValue.from_string("off - - - -")
            self.failUnlessEqual(v.silence_supp_enable, False)
            self.failUnlessEqual(v.silence_timer, None)
            self.failUnlessEqual(v.supp_pref, None)
            self.failUnlessEqual(v.sid_use, None)
            self.failUnlessEqual(v.fxnslevel, None)

    unittest.main()