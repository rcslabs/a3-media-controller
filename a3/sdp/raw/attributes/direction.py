#!/usr/bin/env python
"""
RFC 3264:
    sendrecv
    recvonly
    sendonly
    inactive
"""

from value import FlagAttributeValue


class SendRecvValue(FlagAttributeValue):
    attribute_name = "sendrecv"


class RecvOnlyValue(FlagAttributeValue):
    attribute_name = "recvonly"


class SendOnlyValue(FlagAttributeValue):
    attribute_name = "sendonly"


class InactiveValue(FlagAttributeValue):
    attribute_name = "inactive"



