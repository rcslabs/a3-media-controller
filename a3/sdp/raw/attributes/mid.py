#!/usr/bin/env python
"""
RFC 5888
    The Session Description Protocol (SDP) Grouping Framework
    http://tools.ietf.org/html/rfc5888
"""


from value import StrAttributeValue


class Mid(StrAttributeValue):
    attribute_name = "mid"
