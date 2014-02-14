#!/usr/bin/env python
"""
rfc5888
a=group:<semantics> <identification-tag>
semantics = "LS" / "FID" / semantics-extension

Multiplexing Negotiation Using Session Description Protocol (SDP) Port Numbers
http://tools.ietf.org/html/draft-ietf-mmusic-sdp-bundle-negotiation-04

"""


from value import AttributeValue
from error import ParseError
import collections
import re


class GroupSemanticsValue(str):
    pass


class GroupSemantics:
    LS = GroupSemanticsValue("LS")
    FID = GroupSemanticsValue("FID")
    BUNDLE = GroupSemanticsValue("BUNDLE")

    @classmethod
    def from_string(cls, string):
        assert type(string) is str
        if string == cls.LS:
            return cls.LS
        elif string == cls.FID:
            return cls.FID
        elif string == cls.BUNDLE:
            return cls.BUNDLE
        else:
            raise ParseError("sdp::GroupSemantics is " + repr(string))


class Group(AttributeValue):

    attribute_name = "group"

    def __init__(self, semantics, identification_tags):
        assert type(semantics) is GroupSemanticsValue
        assert isinstance(identification_tags, collections.Iterable)
        self.__semantics = semantics
        self.__identification_tags = identification_tags

    @property
    def semantics(self):
        return self.__semantics

    @property
    def identification_tags(self):
        return self.__identification_tags

    def __str__(self):
        return "%s %s" % (self.__semantics, " ".join(self.__identification_tags))

    @classmethod
    def from_string(cls, string):
        assert type(string) is str
        g = re.match("^(LS|FID|BUNDLE) (.+)$", string)
        if not g:
            raise ParseError("Error parsing group attribute value: " + repr(string))
        return cls(GroupSemantics.from_string(g.group(1)), g.group(2).split(" "))

#TODO: write tests