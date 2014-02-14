#!/usr/bin/env python


from value import AttributeValue
from error import ParseError
import re


class _SrtpCryptoSuiteValue(str):
    pass


class SrtpCryptoSuite:
    """
    srtp-crypto-suite = "AES_CM_128_HMAC_SHA1_32"
                        "F8_128_HMAC_SHA1_32"
                        "AES_CM_128_HMAC_SHA1_80"
                        1*(ALPHA / DIGIT / "_")     -- not supported
    """
    AES_CM_128_HMAC_SHA1_32 = _SrtpCryptoSuiteValue("AES_CM_128_HMAC_SHA1_32")
    F8_128_HMAC_SHA1_32 = _SrtpCryptoSuiteValue("F8_128_HMAC_SHA1_32")
    AES_CM_128_HMAC_SHA1_80 = _SrtpCryptoSuiteValue("AES_CM_128_HMAC_SHA1_80")

    @classmethod
    def from_string(cls, string):
        assert type(string) is str
        if string == cls.AES_CM_128_HMAC_SHA1_32:
            return cls.AES_CM_128_HMAC_SHA1_32
        elif string == cls.F8_128_HMAC_SHA1_32:
            return cls.F8_128_HMAC_SHA1_32
        elif string == cls.AES_CM_128_HMAC_SHA1_80:
            return cls.AES_CM_128_HMAC_SHA1_80
        else:
            raise ParseError("sdp::CryptoSuite is " + repr(string))


class CryptoKeyParams(AttributeValue):
    def __init__(self, key_method, key, lifetime=None, mki=None):
        assert (key_method == "inline")
        assert (type(key) == str)
        assert (lifetime is None or type(lifetime) == str)
        assert (mki is None or type(mki) == str)
        self.__key_method, self.__key, self.__lifetime, self.__mki = key_method, key, lifetime, mki

    def __str__(self):
        result = self.__key_method + ":" + self.__key
        if self.__lifetime:
            result += "|" + self.__lifetime
        if self.__mki:
            result += "|" + self.__mki
        return result

    @property
    def key(self):
        return self.__key

    @classmethod
    def from_string(cls, string):
        assert type(string) is str
        g = re.match("^(inline):([\x21-\x3A,\x3C-\x7E]+?)(?:\|(.+?))?(?:\|(.+?))?$", string)
        if not g:
            raise ParseError("Error parsing CryptoKeyParams value: " + repr(string))
        return cls(g.group(1), g.group(2), g.group(3), g.group(4))

    @classmethod
    def with_key(cls, key):
        return cls("inline", key)


class CryptoSessionParams(AttributeValue):
    """
    rfc4568
        KDR
        UNENCRYPTED_SRTP
        UNENCRYPTED_SRTCP
        UNAUTHENTICATED_SRTP
        FEC_ORDER
        FEC_KEY
        WSH
    """

    def __init__(self, value):
        self.__value = value

    def __str__(self):
        return self.__value

    @classmethod
    def from_string(cls, string):
        assert type(string) is str
        return cls(string)


class CryptoValue(AttributeValue):
    """
    a=crypto:<tag> <crypto-suite> <key-params> [<session-params>]
    a=crypto:1 AES_CM_128_HMAC_SHA1_80 inline:WVNfX19zZW1jdGwgKCkgewkyMjA7fQp9CnVubGVz|2^20|1:32
             KDR=1 UNENCRYPTED_SRTCP
    """

    attribute_name = "crypto"

    def __init__(self, tag, crypto_suite, key_params, session_params=None):
        """Init CryptoValue"""
        assert(type(tag) is int)
        assert(type(crypto_suite) is _SrtpCryptoSuiteValue)
        assert(type(key_params) is CryptoKeyParams)
        assert(session_params is None or type(session_params is CryptoSessionParams))
        self.__tag = tag
        self.__crypto_suite = crypto_suite
        self.__key_params = key_params
        self.__session_params = session_params

    def __str__(self):
        result = "{0} {1} {2}".format(self.__tag, self.__crypto_suite, str(self.__key_params))
        if self.__session_params:
            result += " " + str(self.__session_params)
        return result

    @classmethod
    def from_string(cls, string):
        assert type(string) is str
        g = re.match("^(\d+) (\S+) (\S+)(?: (.+))?$", string)
        if not g:
            raise ParseError("Error parsing CryptoAttribute value: " + repr(string))
        tag = int(g.group(1))
        crypto_suite = SrtpCryptoSuite.from_string(g.group(2))
        key_params = CryptoKeyParams.from_string(g.group(3))
        session_params = CryptoSessionParams.from_string(g.group(4)) if g.group(4) else None
        return cls(tag, crypto_suite, key_params, session_params)

    @property
    def tag(self):
        return self.__tag

    @property
    def crypto_suite(self):
        return self.__crypto_suite

    @property
    def key_params(self):
        return self.__key_params

    @property
    def key(self):
        return self.__key_params.key

    @property
    def session_params(self):
        return self.__session_params


if __name__ == "__main__":
    import unittest

    class CryptoSuiteTest(unittest.TestCase):
        def test_init(self):
            pass

        def test_str(self):
            self.failUnlessEqual(str(SrtpCryptoSuite.AES_CM_128_HMAC_SHA1_32), "AES_CM_128_HMAC_SHA1_32")
            self.failUnlessEqual(str(SrtpCryptoSuite.F8_128_HMAC_SHA1_32), "F8_128_HMAC_SHA1_32")
            self.failUnlessEqual(str(SrtpCryptoSuite.AES_CM_128_HMAC_SHA1_80), "AES_CM_128_HMAC_SHA1_80")

        def test_parse(self):
            self.failUnlessEqual(SrtpCryptoSuite.from_string("AES_CM_128_HMAC_SHA1_32"),
                                 SrtpCryptoSuite.AES_CM_128_HMAC_SHA1_32)
            self.failUnlessEqual(SrtpCryptoSuite.from_string("F8_128_HMAC_SHA1_32"),
                                 SrtpCryptoSuite.F8_128_HMAC_SHA1_32)
            self.failUnlessEqual(SrtpCryptoSuite.from_string("AES_CM_128_HMAC_SHA1_80"),
                                 SrtpCryptoSuite.AES_CM_128_HMAC_SHA1_80)

    class CryptoKeyParamsTest(unittest.TestCase):
        def test_init(self):
            self.failUnlessRaises(AssertionError, CryptoKeyParams, "online", "key")
            CryptoKeyParams("inline", "DOUXfgs9sLB4F16vvCksVKUptM7IptAStkjNS7ky")
            CryptoKeyParams("inline", "key", "2^32")
            self.failUnlessEqual(CryptoKeyParams.with_key("key").key, "key")

        def test_str(self):
            self.failUnlessEqual(str(CryptoKeyParams("inline", "DOUXfgs9sLB4F16vvCksVKUptM7IptAStkjNS7ky")),
                                 "inline:DOUXfgs9sLB4F16vvCksVKUptM7IptAStkjNS7ky")
            self.failUnlessEqual(
                str(CryptoKeyParams("inline", "d0RmdmcmVCspeEc3QGZiNWpVLFJhQX1cfHAwJSoj", "2^20", "1:4")),
                "inline:d0RmdmcmVCspeEc3QGZiNWpVLFJhQX1cfHAwJSoj|2^20|1:4")

        def test_parse(self):
            kp = CryptoKeyParams.from_string("inline:d0RmdmcmVCspeEc3QGZiNWpVLFJhQX1cfHAwJSoj|2^20|1:4")
            self.failUnlessEqual(kp.key, "d0RmdmcmVCspeEc3QGZiNWpVLFJhQX1cfHAwJSoj")
            kp = CryptoKeyParams.from_string("inline:DOUXfgs9sLB4F16vvCksVKUptM7IptAStkjNS7ky")
            self.failUnlessEqual(kp.key, "DOUXfgs9sLB4F16vvCksVKUptM7IptAStkjNS7ky")

    #TODO: CryptoSessionParams

    class CryptoTest(unittest.TestCase):
        def test_init(self):
            pass

        def test_str(self):
            s = "1 AES_CM_128_HMAC_SHA1_80 inline:DOUXfgs9sLB4F16vvCksVKUptM7IptAStkjNS7ky"
            self.failUnlessEqual(str(CryptoValue.from_string(s)), s)
            s = "1 AES_CM_128_HMAC_SHA1_80 inline:PS1uQCVeeCFCanVmcjkpPywjNWhcYD0mXXtxaVBR|2^20|1:32"
            self.failUnlessEqual(str(CryptoValue.from_string(s)), s)

        def test_parse(self):
            c = CryptoValue.from_string(
                "1 AES_CM_128_HMAC_SHA1_80 inline:PS1uQCVeeCFCanVmcjkpPywjNWhcYD0mXXtxaVBR|2^20|1:32")
            self.failUnlessEqual(c.tag, 1)
            self.failUnlessEqual(c.crypto_suite, SrtpCryptoSuite.AES_CM_128_HMAC_SHA1_80)
            self.failUnlessEqual(c.key, "PS1uQCVeeCFCanVmcjkpPywjNWhcYD0mXXtxaVBR")
            c = CryptoValue.from_string(
                "1 AES_CM_128_HMAC_SHA1_80 inline:DOUXfgs9sLB4F16vvCksVKUptM7IptAStkjNS7ky")
            self.failUnlessEqual(c.tag, 1)
            self.failUnlessEqual(c.crypto_suite, SrtpCryptoSuite.AES_CM_128_HMAC_SHA1_80)
            self.failUnlessEqual(c.key, "DOUXfgs9sLB4F16vvCksVKUptM7IptAStkjNS7ky")

    unittest.main()
