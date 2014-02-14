#!/usr/bin/env python
"""



"""


__author__ = 'RCSLabs'


from raw.attribute import Attribute, AttributeCollection, SilenceSuppValue


class SilenceSupp(object):
    def __init__(self, attributes):
        assert type(attributes) is AttributeCollection
        self.__attributes = attributes
        silence_supps = attributes.get("silenceSupp")
        assert len(silence_supps) < 2
        self.__silence_supp_attribute = silence_supps[0] if len(silence_supps) == 1 else None

    def __nonzero__(self):
        return self.__silence_supp_attribute is not None

    @property
    def silence_supp_enable(self):
        if self.__silence_supp_attribute is not None:
            return self.__silence_supp_attribute.value.silence_supp_enable
        else:
            return None

    @silence_supp_enable.setter
    def silence_supp_enable(self, silence_supp_enable):
        assert silence_supp_enable is None or type(silence_supp_enable) is bool
        if silence_supp_enable is not None:
            self.__set_attribute(silence_supp_enable)
        else:
            self.__remove_attribute()

    def __set_attribute(self, silence_supp_enable=False, silence_timer=None, supp_pref=None, sid_use=None,
                        fxnslevel=None):
        if self.__silence_supp_attribute is not None:
            self.__silence_supp_attribute.value.silence_supp_enable = silence_supp_enable
            self.__silence_supp_attribute.value.silence_timer = silence_timer
            self.__silence_supp_attribute.value.supp_pref = supp_pref
            self.__silence_supp_attribute.value.sid_use = sid_use
            self.__silence_supp_attribute.value.fxnslevel = fxnslevel
        else:
            self.__silence_supp_attribute = Attribute("silenceSupp",
                                                      SilenceSuppValue(silence_supp_enable, silence_timer, supp_pref,
                                                                       sid_use, fxnslevel))
            self.__attributes.append(self.__silence_supp_attribute)

    def __remove_attribute(self):
        if self.__ptime_attribute is not None:
            self.__ptime_attribute.remove()
            self.__ptime_attribute = None

