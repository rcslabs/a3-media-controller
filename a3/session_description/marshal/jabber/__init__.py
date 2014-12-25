#!/usr/bin/env python
"""
 Serialize/deserialize session description stored in jabber-xml (XMPP) format

 Mime-type: 'application/jabber+xml'
 http://xmpp.org/extensions/xep-0081.html


"""

__author__ = 'esix'


class JabberMarshal(object):

    @classmethod
    def serialize(cls, session_description):
        raise Exception("Not implemented")

    @classmethod
    def deserialize(cls, xml):
        raise Exception("Not implemented")
