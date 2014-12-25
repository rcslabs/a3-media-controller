#!/usr/bin/env python
"""
 Deserialize SDP text format
 mime-type: Application/sdp

 syntax:
  Request for Comments: 5234
  Augmented BNF for Syntax Specifications: ABNF
  https://tools.ietf.org/html/rfc5234

 rules:
  Request for Comments: 4566
  SDP: Session Description Protocol
  https://tools.ietf.org/html/rfc4566

"""

__author__ = 'esix'


from ...session_description import SessionDescription
from .._base import DeserializeException

from pyparsing import *


# rfc5234
# Augmented BNF for Syntax Specifications: ABNF

# rfc2327
# SDP: Session Description Protocol


_CRLF = "\r\n"
CRLF = lineEnd().suppress()

_tab = "\n"
tab = Literal(_tab).suppress()

_space = " "
space = Literal(_space).suppress()

_safe = alphanums + "''-./:?\"#$&*;=@[]^_`{|}+~"
safe = Word(_safe)
_email_safe = _safe + _space + _tab
email_safe = Word(_email_safe)

ALPHA = Literal("a") | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j" | "k" | \
                 "l" | "m" | "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | \
                 "w" | "x" | "y" | "z" | "A" | "B" | "C" | "D" | "E" | "F" | "G" | \
                 "H" | "I" | "J" | "K" | "L" | "M" | "N" | "O" | "P" | "Q" | "R" | \
                 "S" | "T" | "U" | "V" | "W" | "X" | "Y" | "Z"

POS_DIGIT = Literal("1") | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"

DIGIT = Literal("0") | POS_DIGIT

alpha_numeric = ALPHA | DIGIT

integer = POS_DIGIT + OneOrMore(DIGIT)

text = CharsNotIn("\r\n\0")            # byte-string

ip4_field = Word(nums, max=3)
IP4_address = ip4_field + "." + ip4_field + "." + ip4_field + "." + ip4_field
IP6_address = Word("IP6")   # ;to be defined

nettype = Literal("IN")
addrtype = Literal("IP4") | Literal("IP6")




#
#
#  *(...)    -> ZeroOrMore(...)
#  1*(...)   -> OneOrMore(...)
#  [...]     -> Optional(...)


username = safe       # ;pretty wide definition, but doesn't include space
sess_id = Word(nums)
sess_version = Word(nums)
unicast_address = IP4_address | IP6_address


uri = Word(alphanums + "/:@#")   # ;defined in RFC1630

email = Word(alphanums + "@.")  # ;defined in RFC822

email_address = email | (email + Literal("(") + email_safe + Literal(")")) | (email_safe + Literal("<") + email + Literal(">"))

phone = Literal("+") + POS_DIGIT + OneOrMore(space | "-" | DIGIT)
phone_number = phone | (phone + Literal("(") + email_safe + Literal(")")) | (email_safe + Literal("<") + phone + Literal(">"))

multicast_address = IP4_address

connection_address = multicast_address

bwtype = Word(alphanums)

time = Word(nums)

bandwidth = Word(nums)

fixed_len_time_unit = Literal("d") | Literal("h") | Literal("m") | Literal("s")

typed_time = Word(nums) + Optional(fixed_len_time_unit)

repeat_interval = typed_time

start_time = time | Literal("0")
stop_time = time | Literal("0")

att_value = text
att_field = Word(alphanums + "-")
attribute = (att_field + Literal(":") + att_value) | att_field

media = Word(alphanums)
fmt = Word(alphanums)
port = Word(nums)
proto = Word(alphanums + "/")
media_field = (Literal("m=") + media + space + port + Optional(Literal("/") + Word(nums)) + space + proto + ZeroOrMore(space + fmt) + CRLF).leaveWhitespace()

#
#
#
proto_version = (Literal("v=") + Word(nums) + CRLF).leaveWhitespace()

origin_field = (Literal("o=") + username + space + sess_id + space + sess_version + space + nettype + space + addrtype + space + unicast_address + CRLF).leaveWhitespace()

session_name_field = (Literal("s=") + text + CRLF).leaveWhitespace()

information_field = Optional(Literal("i=") + text + CRLF).leaveWhitespace()

uri_field = Optional(Literal("u=") + uri + CRLF).leaveWhitespace()

email_fields = ZeroOrMore(Literal("e=") + email_address + CRLF)

phone_fields = ZeroOrMore("p=" + phone_number + CRLF)

connection_field = Optional("c=" + nettype + addrtype + connection_address + CRLF)

bandwidth_fields = ZeroOrMore(Literal("b=") + bwtype + Literal(":") + bandwidth + CRLF)

zone_adjustments = Literal("z=") + time + Literal("-") + typed_time + ZeroOrMore(time + Optional(Literal("-")) + typed_time)
repeat_fields = Literal("r=") + repeat_interval + typed_time + OneOrMore(typed_time)
time_fields = OneOrMore(Literal("t=") + start_time + stop_time + ZeroOrMore(CRLF + repeat_fields) + CRLF) + Optional(zone_adjustments + CRLF)

key_data = email_safe | Literal("~") | Empty()
key_type = Literal("prompt") | (Literal("clear:") + key_data) | (Literal("base64:") + key_data) | (Literal("uri:") + uri)
key_field = Optional("k=" + key_type + CRLF)

attribute_fields = ZeroOrMore(Literal("a=") + attribute + CRLF)

media_descriptions = ZeroOrMore(media_field +
                                information_field +
                                connection_field +            # ZeroOrMore(connection_field)  - HANGS
                                bandwidth_fields +
                                key_field +
                                attribute_fields)


announcement = (proto_version +
                origin_field +
                session_name_field +
                information_field +
                uri_field +
                email_fields +
                phone_fields +
                connection_field +
                bandwidth_fields +
                time_fields +
                key_field +
                attribute_fields +
                media_descriptions)    #.leaveWhitespace()

parser = stringStart + announcement + stringEnd


level = 0


class TreeChild(object):
    def __init__(self, t):
        self.args = t

    def __str__(self):
        ret = " %s: " % self.name
        return '[' + ' ' * level + ret + self.args[0] + "]\n"


class TreeBranch(object):
    def __init__(self, t):
        self.args = t

    def __str__(self):
        global level
        level = level + 1
        childs = " ".join(map(str, self.args))
        level = level - 1
        ret = " %s: " % self.name + '\n'
        return ' ' * level + ret + childs + "\n"


class AST_Sdp(TreeBranch):
    name = 'SDP'

    def __str__(self):
        medias = filter(lambda item: isinstance(item, AST_Media), self.args)
        return "MEDIAS:" + ", ".join(map(str, medias))


class AST_Media(TreeBranch):
    name = 'media'


class Attribute(TreeBranch):
    name = "attribute"


announcement.setParseAction(AST_Sdp)
media_descriptions.setParseAction(AST_Media)
attribute.setParseAction(Attribute)


def deserialize_sdp(text):
    assert type(text) is str
    try:
        ast_sdp = parser.parseString(text)[0]
    except ParseException:
        raise DeserializeException()

    print str(ast_sdp)

    session_description = SessionDescription()

    # build sdp based on ast_sdp
    return session_description

