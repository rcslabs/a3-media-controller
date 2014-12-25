#!/usr/bin/env python
"""
    Session description marshal module
    Currently implemented only for mime-type: 'application/sdp'
"""

__author__ = 'esix'


SDP_MIME_TYPE = 'application/sdp'
JABBER_MIME_TYPE = 'application/jabber+xml'


from .sdp import SdpMarshal
# from .jabber import JabberMarshal
from ._base import DeserializeException, SerializeException


class Marshal(object):
    """
    Common serializer/deserializer for session_description
    uses mime_type to select concrete serializer/deserializer
    if none found raises SerializeException/DeserializeException
    """

    @classmethod
    def serialize(cls, session_description, mime_type=SDP_MIME_TYPE):
        if mime_type == SDP_MIME_TYPE:
            return SdpMarshal.serialize(session_description)
        else:
            raise SerializeException()

    @classmethod
    def deserialize(cls, text, mime_type=SDP_MIME_TYPE):
        if mime_type == SDP_MIME_TYPE:
            return SdpMarshal.deserialize(text)
        else:
            raise DeserializeException()

