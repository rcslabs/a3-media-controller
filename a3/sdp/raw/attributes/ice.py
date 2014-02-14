#!/usr/bin/env python
"""
RFC 5245


Interactive Connectivity Establishment (ICE): A Protocol for Network
Address Translator (NAT) Traversal for Offer/Answer Protocols
     http://tools.ietf.org/html/draft-ietf-mmusic-ice-19


ice-lite:
    Implementing Interactive Connectivity Establishment (ICE) in Lite Mode
    http://tools.ietf.org/html/draft-rescorla-mmusic-ice-lite-00


ice-mismatch:
    http://tools.ietf.org/html/draft-ietf-mmusic-ice-19


ice-options           = "ice-options" ":" ice-option-tag
                             0*(SP ice-option-tag)
ice-option-tag        = 1*ice-char


TODO: add candidate value as http://tools.ietf.org/html/rfc5245#section-15.1


"""


from value import FlagAttributeValue, StrAttributeValue


class IceLiteValue(FlagAttributeValue):
    attribute_name = "ice-lite"


class IceMismatchValue(FlagAttributeValue):
    attribute_name = "ice-mismatch"


class IceUfragValue(StrAttributeValue):
    attribute_name = "ice-ufrag"


class IcePwdValue(StrAttributeValue):
    attribute_name = "ice-pwd"


class IceOptionsValue(StrAttributeValue):
    attribute_name = "ice-options"


#class CandidateValue(AttributeValue):
#    def __init__(self):
#        self._component = '1'
#        self._foundation = '1'
#        self._generation = '0'
#        self._id = 'el0747fg11'
#        self._ip = '10.0.1.1'
#        self._network = '1'
#        self._port = '8998'
#        self._priority = '2130706431'
#        self._protocol = 'udp'
#        self._type = 'host'
#
##        <candidate component='1'
##                   foundation='1'
##                   generation='0'
##                   id='el0747fg11'
##                   ip='10.0.1.1'
##                   network='1'
##                   port='8998'
##                   priority='2130706431'
##                   protocol='udp'
##                   type='host'/>
##        <candidate component='1'
##                   foundation='2'
##                   generation='0'
##                   id='y3s2b30v3r'
##                   ip='192.0.2.3'
##                   network='1'
##                   port='45664'
##                   priority='1694498815'
##                   protocol='udp'
##                   rel-addr='10.0.1.1'
##                   rel-port='8998'
##                   type='srflx'/>
##
##
