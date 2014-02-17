#!/usr/bin/env python
"""
SDP entities classes
    Each class has class method from_string
    which can throw SdpParseError

classes:
    ProtocolVersionValue                +
    OriginValue                         +
    SessionNameValue                    +
    SessionInformationValue
    UriValue
    EmailAddressValue
    PhoneNumberValue
    ConnectionDataValue                 +
    TimingValue                         +
    RepeatTimesValue
    TimeZoneValue
    EncryptionKeysValue
    MediaDescriptionValue
"""

from attributes.error import ParseError
from attributes.common import *
from a3.media import MediaType

import re
import collections


class MediaDescriptionProtoValue(str):
    pass


class MediaDescriptionProto:
    """
    Profiles:
    RTP/AVP
    RTP/AVPF
    RTP/SAVP
    RTP/SAVPF
    SCTP/DTLS
    udp

    Additional:
    RTMP

    TODO:
    profiles should be list as there might be many values
    """
    RTP_AVP = MediaDescriptionProtoValue("RTP/AVP")
    RTP_SAVPF = MediaDescriptionProtoValue("RTP/SAVPF")
    RTMP = MediaDescriptionProtoValue("RTMP")

    @classmethod
    def from_string(cls, string):
        assert type(string) is str
        if string == cls.RTP_AVP:
            return cls.RTP_AVP
        elif string == cls.RTP_SAVPF:
            return cls.RTP_SAVPF
        elif string == cls.RTMP:
            return cls.RTMP
        else:
            raise ParseError("MediaDescription Proto is " + repr(string))


class ProtocolVersion(object):
    """
    v=0
    """

    def __init__(self, v):
        assert(v == 0)
        self.__version = v

    @property
    def version(self):
        return self.__version

    def __str__(self):
        return str(self.__version)

    @classmethod
    def from_string(cls, string):
        assert type(string) is str
        g = re.match("^(\d+)$", string)
        if not g or g.group(1) != "0":
            raise ParseError("Error parsing ProtocolVersionValue: " + repr(string))
        return cls(int(g.group(1)))


class Origin(object):
    """
    o=<username> <sess-id> <sess-version> <nettype> <addrtype> <unicast-address>
    """

    def __init__(self, username, sess_id, sess_version, nettype, addrtype, unicast_address):
        assert type(username) is str
        assert type(sess_id) is str
        assert type(sess_version) is str
        assert type(nettype) is NetTypeValue
        assert type(addrtype) is AddrTypeValue
        assert type(unicast_address) is str
        self.__username = username
        self.__sess_id = sess_id
        self.__sess_version = sess_version
        self.__nettype = nettype
        self.__addrtype = addrtype
        self.__unicast_address = unicast_address

    def __str__(self):
        return "{0} {1} {2} {3} {4} {5}".format(self.__username, self.__sess_id, self.__sess_version,
                                                str(self.__nettype), str(self.__addrtype), self.__unicast_address)

    @classmethod
    def from_string(cls, string):
        assert type(string) is str
        g = re.match("^(\S+) (\d+) (\d+) (\S+) (\S+) (\S+)$", string)
        if not g:
            raise ParseError("Error parsing OriginValue: " + repr(string))
        return cls(g.group(1), g.group(2), g.group(3),
                   NetType.from_string(g.group(4)), AddrType.from_string(g.group(5)), g.group(6))

    @property
    def username(self):
        return self.__username

    @property
    def sess_id(self):
        return self.__sess_id

    @property
    def sess_version(self):
        return self.__sess_version

    @property
    def nettype(self):
        return self.__nettype

    @property
    def addrtype(self):
        return self.__addrtype

    @property
    def unicast_address(self):
        return self.__unicast_address

    @unicast_address.setter
    def unicast_address(self, unicast_address):
        assert type(unicast_address) is str
        self.__unicast_address = unicast_address


class SessionName(object):
    """
    s=<session name>
    """

    def __init__(self, session_name):
        assert(type(session_name) is str)
        self.__session_name = session_name

    def __str__(self):
        return self.__session_name

    @property
    def session_name(self):
        return self.__session_name

    @session_name.setter
    def session_name(self, session_name):
        self.__session_name = session_name

    @property
    def value(self):
        return self.__session_name

    @value.setter
    def value(self, session_name):
        self.__session_name = session_name

    @classmethod
    def from_string(cls, string):
        assert type(string) is str
        return cls(string)


#Session Information ("i=")
#   i=<session description>
#There MUST be at most one session-level "i=" field per session description,   and at most one "i=" field per media.
class SessionInformation(object):
    pass


# URI ("u=")        OPTIONAL
#      u=<uri>
class Uri(object):
    pass


#5.6.  Email Address and Phone Number ("e=" and "p=")
#     e=<email-address>
#    p=<phone-number>
class EmailAddress(object):
    pass


class PhoneNumber(object):
    pass


class ConnectionData(object):
    """
    c=<nettype> <addrtype> <connection-address>
    """

    def __init__(self, nettype, addrtype, connection_address):
        assert type(nettype) is NetTypeValue
        assert type(addrtype) is AddrTypeValue
        assert type(connection_address) is str
        self.__nettype, self.__addrtype,  self.__connection_address = nettype, addrtype, connection_address

    def __str__(self):
        return "{0} {1} {2}".format(self.__nettype, self.__addrtype, self.__connection_address)

    @property
    def connection_address(self):
        return self.__connection_address

    @connection_address.setter
    def connection_address(self, val):
        assert(type(val) is str)
        self.__connection_address = val

    @classmethod
    def from_string(cls, string):
        assert type(string) is str
        g = re.match("^(\S+) (\S+) (\S+)$", string)
        if not g:
            raise ParseError("Error parsing ConnectionDataValue: " + repr(string))
        return cls(NetType.from_string(g.group(1)), AddrType.from_string(g.group(2)), g.group(3))


# 5.8. Bandwidth
# b=<bwtype>:<bandwidth>
#b=AS:1273 
#b=TIAS:1214000 
#b=RS:75875
class Bandwidth:
    pass


class Timing(object):
    """
    t=<start-time> <stop-time>
    """

    def __init__(self, start_time, stop_time):
        assert(type(start_time) is long)
        assert(type(stop_time) is long)
        self.__start_time, self.__stop_time = start_time, stop_time

    def __str__(self):
        return "{0} {1}".format(self.__start_time, self.__stop_time)

    @property
    def start_time(self):
        return self.__start_time

    @property
    def stop_time(self):
        return self.__stop_time

    @classmethod
    def from_string(cls, string):
        assert type(string) is str
        g = re.match("^(\d+) (\d+)$", string)
        if not g:
            raise ParseError("Error parsing TimingValue: " + repr(string))
        return cls(long(g.group(1)), long(g.group(2)))


class TypedTime(object):
    """
    typed-time = 1*DIGIT [fixed-len-time-unit]
    """
    SPECIFICATION_CHARACTERS = {
        "d": 86400L,
        "h": 3600L,
        "m": 60L,
        "s": 1L,
        None: 1L
    }

    def __init__(self, value, len_time_unit=None):
        assert(type(value) is long)
        assert(len_time_unit is None or len_time_unit in ("d", "h", "m", "s"))
        self.__value, self.__len_time_unit = value, len_time_unit

    def __str__(self):
        return str(self.__value) + (self.__len_time_unit if self.__len_time_unit is not None else "")

    @property
    def value(self):
        return self.__value * TypedTime.SPECIFICATION_CHARACTERS[self.__len_time_unit]

    @classmethod
    def from_string(cls, string):
        assert type(string) is str
        g = re.match("^(\d+)([dhms])?$", string)
        if not g:
            raise ParseError("Error parsing TimingValue: " + repr(string))
        return cls(long(g.group(1)), g.group(2))


class RepeatTimes(object):
    """
    r=<repeat interval> <active duration> <offsets from start-time>
    """

    def __init__(self, repeat_interval, active_duration, offsets):
        assert(type(repeat_interval) is TypedTime)
        assert(type(active_duration) is TypedTime)
        assert(isinstance(offsets, collections.Iterable) and
               type(offsets) is not str and
               not [o for o in offsets if type(o) is not TypedTime])
        self.__repeat_interval, self.__active_duration, self.__offsets = repeat_interval, active_duration, offsets

    def __str__(self):
        return "{0} {1} {2}".format(self.__repeat_interval, self.__active_duration, " ".join(map(str, self.__offsets)))

    @classmethod
    def from_string(cls, string):
        assert type(string) is str
        g = re.match("^(\d+[dhms]?) (\d+[dhms]?)((?: \d+[dhms]?)+)$", string)
        if not g:
            raise ParseError("Error parsing RepeatTimesValue: " + repr(string))
        str_offsets = g.group(3)[1:].split(" ")
        return cls(TypedTime.from_string(g.group(1)),
                   TypedTime.from_string(g.group(2)),
                   map(TypedTime.from_string, str_offsets))


class TimeDescription:
    """
    t=  (time the session is active)
    r=* (zero or more repeat times)
    """

    def __init__(self, timing_value, repeat_times=None):
        assert(type(timing_value) is Timing)
        assert(repeat_times is None or
               (isinstance(repeat_times, collections.Iterable) and
                type(repeat_times) is not str and
                not [o for o in repeat_times if type(o) is not RepeatTimes]))
        self.__timing_value, self.__repeat_times = timing_value, (repeat_times or [])

    def add_repeat_times(self, repeat_times):
        assert type(repeat_times) is RepeatTimes
        self.__repeat_times.append(repeat_times)

    def to_str_list(self):
        return ["t=" + str(self.__timing_value)] + ["r=" + str(rt) for rt in self.__repeat_times]

    def __str__(self):
        return "\r\n".join(self.to_str_list()) + "\r\n"


# 5.11.  Time Zones ("z=")
#  z=<adjustment time> <offset> <adjustment time> <offset> ....
class TimeZone(object):
    pass


#5.12.  Encryption Keys ("k=")
#     k=<method>
#     k=<method>:<encryption key>
class EncryptionKeys(object):
    pass


# 5.13.  Attributes ("a=")
#
#


#5.14.  Media Descriptions ("m=")
#      m=<media> <port> <proto> <fmt> ...
class MediaDescription(object):
    """
    m=<media> <port> <proto> <fmt> ...
    """
    def __init__(self, media_type, port, proto, fmt):
        """
        Initializes media description value
        """
        assert type(media_type) is MediaType
        assert type(port) is int
        assert type(proto) is MediaDescriptionProtoValue
        assert type(fmt) is list
        self.__media_type, self.__port, self.__proto, self.__fmt = media_type, port, proto, fmt

    @property
    def media_type(self):
        return self.__media_type

    @media_type.setter
    def media_type(self, media_type):
        assert type(media_type) is MediaType
        self.__media_type = media_type

    @property
    def port(self):
        return self.__port

    @port.setter
    def port(self, val):
        assert type(val) is int
        self.__port = val

    @property
    def proto(self):
        return self.__proto

    @proto.setter
    def proto(self, proto):
        assert type(proto) is MediaDescriptionProtoValue
        self.__proto = proto

    @property
    def fmt(self):
        return self.__fmt

    @fmt.setter
    def fmt(self, val):
        assert type(val) is list
        self.__fmt = val

    def add_fmt_item(self, val):
        self.__fmt.append(val)

    def __str__(self):
        return "{0} {1} {2} {3}".format(self.media_type, self.port, str(self.proto), " ".join(map(str, self.fmt)))

    @classmethod
    def from_string(cls, string):
        assert type(string) is str
        g = re.match("^(\w+) (\d+) (\S+) (.+)$", string)
        if not g:
            raise ParseError("Error parsing MediaDescriptionValue: " + repr(string))
        fmt = map(int, g.group(4).split(" "))
        try:
            return cls(MediaType.from_string(g.group(1)),
                       int(g.group(2)),
                       MediaDescriptionProto.from_string(g.group(3)),
                       fmt)
        except AssertionError:
            raise ParseError("Error parsing MediaDescriptionValue: " + repr(string))


if __name__ == "__main__":
    import unittest

    class ProtocolVersionValueTest(unittest.TestCase):
        def test_init(self):
            self.failUnlessRaises(AssertionError, ProtocolVersion, "0")
            self.failUnlessRaises(AssertionError, ProtocolVersion, None)
            self.failUnlessRaises(AssertionError, ProtocolVersion, 1)
            ProtocolVersion(0)

        def test_str(self):
            self.failUnlessEqual(str(ProtocolVersion.from_string("0")), "0")

        def test_parse(self):
            self.failUnlessRaises(ParseError, ProtocolVersion.from_string, "1")
            self.failUnlessRaises(ParseError, ProtocolVersion.from_string, "")
            self.failUnlessEqual(ProtocolVersion.from_string("0").version, 0)

    class OriginValueTest(unittest.TestCase):
        def test_init(self):
            self.failUnlessRaises(AssertionError,
                                  Origin, "-", "3229174452", "2", "IN", "IP4", "127.0.0.1")
            self.failUnlessRaises(AssertionError,
                                  Origin, "-", 3229174452, "2", NetType.IN, AddrType.IP4, "127.0.0.1")
            Origin("-", "3229174452", "2", NetType.IN, AddrType.IP4, "127.0.0.1")

        def test_str(self):
            self.failUnlessEqual(str(Origin.from_string("1012 0 0 IN IP4 192.168.1.36")),
                                 "1012 0 0 IN IP4 192.168.1.36")
            self.failUnlessEqual(str(Origin.from_string("- 3229174452 2 IN IP4 127.0.0.1")),
                                 "- 3229174452 2 IN IP4 127.0.0.1")

        def test_parse(self):
            self.failUnlessRaises(ParseError, Origin.from_string, "- 3229174452 2 IN IP4 127.0.0.1 ")
            self.failUnlessRaises(ParseError, Origin.from_string, " - 3229174452 2 IN IP4 127.0.0.1")

            v = Origin.from_string("- 3229174452 2 IN IP4 127.0.0.1")
            self.failUnlessEqual(v.username,         "-")
            self.failUnlessEqual(v.sess_id,          "3229174452")
            self.failUnlessEqual(v.sess_version,     "2")
            self.failUnlessEqual(v.nettype,          NetType.IN)
            self.failUnlessEqual(v.addrtype,         AddrType.IP4)
            self.failUnlessEqual(v.unicast_address,  "127.0.0.1")

            v = Origin.from_string("1012 0 0 IN IP4 192.168.1.36")
            self.failUnlessEqual(v.username,        "1012")
            self.failUnlessEqual(v.sess_id,          "0")
            self.failUnlessEqual(v.sess_version,     "0")
            self.failUnlessEqual(v.nettype,          NetType.IN)
            self.failUnlessEqual(v.addrtype,         AddrType.IP4)
            self.failUnlessEqual(v.unicast_address,  "192.168.1.36")

    class SessionNameValueTest(unittest.TestCase):
        def test_init(self):
            self.failUnlessRaises(AssertionError, SessionName, None)
            self.failUnlessRaises(AssertionError, SessionName, 12)
            SessionName(" ")

        def test_str(self):
            self.failUnlessEqual(str(SessionName.from_string("")),  "")
            self.failUnlessEqual(str(SessionName.from_string("x")), "x")

        def test_parse(self):
            self.failUnlessEqual(SessionName.from_string("").session_name,  "")
            self.failUnlessEqual(SessionName.from_string("x").session_name, "x")

    class ConnectionDataValueTest(unittest.TestCase):
        pass

    class TimingValueTest(unittest.TestCase):
        def test_init(self):
            self.failUnlessRaises(AssertionError, Timing, 0, 0)
            self.failUnlessRaises(AssertionError, Timing, "x", 0)
            Timing(0L, 0L)

        def test_str(self):
            self.failUnlessEqual(str(Timing(0L, 0L)),       "0 0")
            self.failUnlessEqual(str(Timing(0L, 100000L)),  "0 100000")
            self.failUnlessEqual(str(Timing(-1L, 100000L)), "-1 100000")

        def test_parse(self):
            self.failUnlessRaises(ParseError, Timing.from_string, " 0 0")
            self.failUnlessRaises(ParseError, Timing.from_string, "0 0 ")
            self.failUnlessRaises(ParseError, Timing.from_string, "0  0")

            t = Timing.from_string("0 0")
            self.failUnlessEqual(t.start_time, 0L)
            self.failUnlessEqual(t.stop_time,  0L)

            t = Timing.from_string("10 10000")
            self.failUnlessEqual(t.start_time, 10L)
            self.failUnlessEqual(t.stop_time, 10000L)

    class TypedTimeTest(unittest.TestCase):
        def test_init(self):
            self.failUnlessRaises(AssertionError, TypedTime, 0)
            self.failUnlessRaises(AssertionError, TypedTime, 0, "s")
            self.failUnlessRaises(AssertionError, TypedTime, 1L, "x")
            TypedTime(0L)
            TypedTime(31L,  "d")
            TypedTime(1L,   "h")
            TypedTime(600L, "m")
            TypedTime(60L,  "s")

        def test_str(self):
            self.failUnless(str(TypedTime(0L)) == "0")
            self.failUnless(str(TypedTime(10L, "s")) == "10s")
            self.failUnless(str(TypedTime(1L,"d")) == "1d")

        def test_parse(self):
            self.failUnlessRaises(ParseError, TypedTime.from_string, "d")
            self.failUnlessRaises(ParseError, TypedTime.from_string, "-10")
            self.failUnlessEqual(str(TypedTime.from_string("1d")),  "1d")
            self.failUnlessEqual(str(TypedTime.from_string("0s")),  "0s")
            self.failUnlessEqual(str(TypedTime.from_string("24h")), "24h")
            self.failUnlessEqual(str(TypedTime.from_string("60m")), "60m")
            self.failUnlessEqual(str(TypedTime.from_string("100")), "100")

        def test_value(self):
            self.failUnlessEqual(TypedTime(100L).value,     100)
            self.failUnlessEqual(TypedTime(7L, "d").value,  604800)
            self.failUnlessEqual(TypedTime(1L, "h").value,  3600)
            self.failUnlessEqual(TypedTime(0L).value,       0)
            self.failUnlessEqual(TypedTime(25L, "h").value, 90000)

    class RepeatTimesValueTest(unittest.TestCase):
        def test_init(self):
            _0 = TypedTime(0L)
            _3 = TypedTime(3L)
            self.failUnlessRaises(AssertionError, RepeatTimes, _0, _0, None)
            self.failUnlessRaises(AssertionError, RepeatTimes, _0, _0, "Error")
            self.failUnlessRaises(AssertionError, RepeatTimes, _0, _0, [_0, "Error", _3])
            RepeatTimes(_0, _3, [_0, _3])
            RepeatTimes(_0, _3, [])

        def test_str(self):
            _7d = TypedTime(7L, "d")
            _1h = TypedTime(1L, "h")
            _0 = TypedTime(0L)
            _25h = TypedTime(25L, "h")
            self.failUnlessEqual(str(RepeatTimes(_7d, _1h, [_0, _25h])), "7d 1h 0 25h")

        def test_parse(self):
            self.failUnlessRaises(ParseError, RepeatTimes.from_string,      "10 10")
            self.failUnlessRaises(ParseError, RepeatTimes.from_string,      "0d 1h")
            self.failUnlessEqual(str(RepeatTimes.from_string("7d 1h 0 25h")),  "7d 1h 0 25h")
            self.failUnlessEqual(str(RepeatTimes.from_string("7d 1h 25h")),    "7d 1h 25h")
            self.failUnlessEqual(str(RepeatTimes.from_string("0 0 0")),        "0 0 0")

    class TimeDescriptionTest(unittest.TestCase):
        def test_init(self):
            TimeDescription(Timing(0L, 0L), [])
            TimeDescription(Timing(0L, 0L))

        def test_str(self):
            self.failUnlessEqual(str(TimeDescription(Timing(0L, 0L), [])), "t=0 0\r\n")
            td = TimeDescription(Timing(0L, 0L), [RepeatTimes.from_string("7d 1h 0 25h"),
                                                  RepeatTimes.from_string("7d 1h 0 26h")])
            self.failUnlessEqual(str(td), "t=0 0\r\n"
                                          "r=7d 1h 0 25h\r\n"
                                          "r=7d 1h 0 26h\r\n")

    class MediaDescriptionValueTest(unittest.TestCase):
        def test_init(self):
            self.failUnlessRaises(AssertionError, MediaDescription, "wrong", 1, MediaDescriptionProto.RTP_AVP, [96])
            self.failUnlessRaises(AssertionError, MediaDescription, "audio", 1, "wrong", [96])
            m = MediaDescription(MediaType.VIDEO, 1, MediaDescriptionProto.RTP_AVP, [96, 97])
            for wrong_media_value in ("wrong", None, 42):
                try:
                    m.media_type = wrong_media_value
                except AssertionError:
                    pass
                else:
                    self.fail("Did not see Value error at m.media setter")

            m.media_type = MediaType.APPLICATION
            m.port = 50002
            m.proto = MediaDescriptionProto.RTP_SAVPF
            m.fmt = [97, 98]
            self.failUnlessEqual(m.media_type, "application")
            self.failUnlessEqual(m.port, 50002)
            self.failUnlessEqual(m.proto, MediaDescriptionProto.RTP_SAVPF)
            self.failUnlessEqual(m.fmt, [97, 98])

        def test_str(self):
            self.failUnlessEqual(str(MediaDescription.from_string("audio 1 RTP/SAVPF 9")), "audio 1 RTP/SAVPF 9")
            self.failUnlessEqual(str(MediaDescription.from_string("video 10 RTP/AVP 9 10")), "video 10 RTP/AVP 9 10")

        def test_parse(self):
            self.failUnlessRaises(ParseError, MediaDescription.from_string, "video 1 RTP/XAVP 96 97")
            self.failUnlessRaises(ParseError, MediaDescription.from_string, "application 1 RTP/SAVP")
            self.failUnlessRaises(ParseError, MediaDescription.from_string, "virus 1 RTP/SAVP")
            self.failUnlessRaises(ParseError, MediaDescription.from_string, " video 1 RTP/SAVP 96 97")

            m = MediaDescription.from_string("audio 1 RTP/SAVPF 9")
            self.failUnlessEqual(m.media_type, "audio")
            self.failUnlessEqual(m.port,  1)
            self.failUnlessEqual(m.proto, MediaDescriptionProto.RTP_SAVPF)
            self.failUnlessEqual(m.fmt,   [9])

    unittest.main()
