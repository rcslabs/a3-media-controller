#!/usr/bin/env python
"""

"""

__author__ = 'esix'

from ._serialize import serialize_sdp
from ._deserialize import deserialize_sdp


class SdpMarshal(object):

    @classmethod
    def serialize(cls, session_description):
        return serialize_sdp(session_description)

    @classmethod
    def deserialize(cls, text):
        return deserialize_sdp(text)

