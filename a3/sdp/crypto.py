#!/usr/bin/env python
"""
rfc4568

TODO: For now we guess that there is only one crypto attribute
But there might be many of them
"""


from raw.attribute import Attribute, AttributeCollection
from error import SemanticError
from raw.attributes.crypto import CryptoValue, SrtpCryptoSuite, CryptoKeyParams


class Crypto(object):
    def __init__(self, attributes):
        assert type(attributes) is AttributeCollection
        self.__attributes = attributes
        cryptos = attributes.get("crypto")
        if len(cryptos) > 1:
            raise SemanticError("More then one crypto in SDP: " + str(len(cryptos)))
        self.__attribute = cryptos[0] if len(cryptos) == 1 else None

    def __nonzero__(self):
        return bool(self.__attribute)

    def remove(self):
        if self.__attribute is not None:
            self.__attribute.remove()
            self.__attribute = None

    @property
    def crypto_suite(self):
        return self.__attribute.value.crypto_suite if self.__attribute else None

    @property
    def key_params(self):
        return self.__attribute.value.key_params if self.__attribute else None

    @property
    def key(self):
        return self.__attribute.value.key if self.__attribute else None

    @property
    def session_params(self):
        return self.__attribute.value.session_params if self.__attribute else None

    def generate_AES_CM_128_HMAC_SHA1_80(self):
        if self.__attribute is None:
            value = CryptoValue(1,
                                SrtpCryptoSuite.AES_CM_128_HMAC_SHA1_80,
                                CryptoKeyParams.with_key("DOUXfgs9sLB4F16vvCksVKUptM7IptAStkjNS7ky"))
            self.__attribute = Attribute("crypto", value)
            self.__attributes.append(self.__attribute)

#TODO: write tests