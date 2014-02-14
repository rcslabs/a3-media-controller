#!/usr/bin/env python


from attributes.error import ParseError
import attribute
import entity
import media
import sdp
import re


class AttributesParser(object):
    """
    a=<attribute>
    a=<attribute>:<value>
    """

    def __init__(self):
        self.__attributes = attribute.AttributeCollection()

    @property
    def attributes(self):
        return self.__attributes

    def line(self, t, v):
        if t == "$":                                                            # EOF marker
            return
        self.__attributes.append(attribute.Attribute.from_string(v))


class MediaParserStateMachine(object):
    def __init__(self):
        self.__media = None
        self.__attributes_parser = AttributesParser()
        self.__prev_t = ""

    @property
    def media(self):
        return self.__media

    def line(self, t, v):
        prev = self.__prev_t

        if (prev == "" and t in "m" or
           prev == "m" and t in "icbka$" or
           prev == "i" and t in "cbka$" or
           prev == "c" and t in "bka$" or
           prev == "b" and t in "bka$" or
           prev == "k" and t in "a$" or
           prev == "a" and t in "a$"):
            self.__reg(t, v)
        else:
            raise ParseError("Error parsing sdp media: unexpected line " + repr(t) + ":" + repr(v))

        self.__prev_t = t

    def __reg(self, t, v):
        if t == "m":
            self.__media = media.Media(media_description=entity.MediaDescription.from_string(v))
        elif t == "i":
            pass
        elif t == "c":
            self.__media.connection_data = entity.ConnectionData.from_string(v)
        elif t == "b":
            pass
        elif t == "k":
            pass
        elif t == "a":
            self.__attributes_parser.line(t, v)
        elif t == "$":
            self.__attributes_parser.line(t, v)
            self.__media.attributes = self.__attributes_parser.attributes
        else:
            raise ParseError("Unknown sdp media parameter: " + repr(t) + "=" + repr(v))


class SdpParserStateMachine(object):
    def __init__(self):
        self.__sdp = sdp.Sdp()
        self.__sdp.time_descriptions = []
        self.__prev = ""
        self.__media_parser = None
        self.__time_description = None
        self.__sdp.__time_descriptions = []

    @property
    def sdp(self):
        return self.__sdp

    def line(self, t, v):
        prev = self.__prev

        if self.__media_parser and t not in "m$":                           # if m or EOF then we take care of that line
            self.__media_parser.line(t, v)                                   # otherwize pass it to media parser

        elif prev == "" and t in "v":
            self.__reg(t, v)
        elif prev == "v" and t in "o":
            self.__reg(t, v)
        elif prev == "o" and t in "s":
            self.__reg(t, v)
        elif prev == "s" and t in "iuepcbt":
            self.__reg(t, v)
        elif prev == "i" and t in "uepcbt":
            self.__reg(t, v)
        elif prev == "u" and t in "epcbt":
            self.__reg(t, v)
        elif prev == "e" and t in "pcbt":
            self.__reg(t, v)
        elif prev == "p" and t in "cbt":
            self.__reg(t, v)
        elif prev == "c" and t in "bt":
            self.__reg(t, v)
        elif prev == "b" and t in "bt":
            self.__reg(t, v)                          # b=* (zero or more bandwidth information lines)
        elif prev == "t" and t in "trzakam$":
            self.__reg(t, v)                           # after t : zero or more repeat r=...
        elif prev == "r" and t in "trzakam$":
            self.__reg(t, v)
        elif prev == "z" and t in "kam$":
            self.__reg(t, v)
        elif prev == "k" and t in "am$":
            self.__reg(t, v)
        elif prev == "a" and t in "am$":
            self.__reg(t, v)
        elif prev == "m" and t in "m$":
            self.__reg(t, v)           # after m: only other m or EOF
        else:
            raise ParseError("Error parsing sdp: unexpected line " + repr(t) + ":" + repr(v))

        self.__prev = t

    def __reg(self, t, v):
        if t == "v":
            self.__sdp.protocol_version = entity.ProtocolVersion.from_string(v)
        elif t == "o":
            self.__sdp.origin_value = entity.Origin.from_string(v)
        elif t == "s":
            self.__sdp.session_name = entity.SessionName.from_string(v)
        elif t == "i":
            pass
        elif t == "u":
            pass
        elif t == "e":
            pass
        elif t == "p":
            pass
        elif t == "c":
            self.__sdp.connection_data = entity.ConnectionData.from_string(v)
        elif t == "b":
            pass
        elif t == "t":
            self.__time_description_finished(t, v)
        elif t == "r":
            self.__time_description.add_repeat_times(entity.RepeatTimes.from_string(v))
        elif t == "z":
            pass
        elif t == "k":
            pass
        elif t == "a":
            pass
        elif t == "m":
            self.__media_finished(t, v)
        elif t == "$":
            self.__media_finished(t, v)
        else:
            raise ParseError("Unknown sdp parameter: " + repr(t) + "=" + repr(v))

    def __media_finished(self, t, v):
        if self.__media_parser:
            self.__media_parser.line("$", None)                                  # finalize current media if any
            self.__sdp.medias.append(self.__media_parser.media)
        self.__media_parser = None
        if t == "m":                                                            # and start new media if necessary
            self.__media_parser = MediaParserStateMachine()
            self.__media_parser.line(t, v)

        self.__time_description_finished(t, v)

    def __time_description_finished(self, t, v):
        if self.__time_description:
            self.__sdp.time_descriptions.append(self.__time_description)
            self.__time_description = None
        if t == "t":
            self.__time_description = entity.TimeDescription(entity.Timing.from_string(v), [])


def parse_sdp(sdp_str):
    assert type(sdp_str) is str
    sm = SdpParserStateMachine()

    for line in sdp_str.splitlines():
        g = re.match("^(\w)=(.+)$", line)
        if not g:
            raise ParseError("Error parsing sdp at line" + repr(line))
        t, v = g.groups()
        sm.line(t, v)

    sm.line("$", None)    # end of lines

    return sm.sdp


if __name__ == "__main__":
    import unittest

    def compare_line_by_line(l1, l2):
        for i in range(max(len(l1), len(l2))):
            s = "-"
            if i < len(l1) and i < len(l2) and l1[i] == l2[i]:
                s = "+"
            r1 = repr(l1[i]) if i < len(l1) else " "
            r2 = repr(l2[i]) if i < len(l2) else " "
            print "{0:>3} {1:^3} {2:30} {3:30}".format(i, s, r1, r2)

    class ParseSdpTest(unittest.TestCase):
        def test(self):
            self.failUnlessRaises(ParseError, parse_sdp, "")

            str_sdp = "\r\n".join([
                "v=0",
                "o=1010 0 0 IN IP4 127.0.0.1",
                "s=Session SIP/SDP",
                "c=IN IP4 127.0.0.1",
                "t=0 0",
                "r=7d 1h 0 25h",
                "r=604800 3600 0 90000",
                "t=0 10000",
                "r=7d 1h 0 25h",
                "r=604800 3600 0 90000",
                "m=audio 55000 RTP/AVP 8 101",
                "a=rtpmap:8 PCMA/8000/1",
                "a=rtpmap:101 telephone-event/8000/1",
                "a=fmtp:101 0-15",
                "a=sendrecv",
                "a=ptime:20",
                "a=silenceSupp:off - - - -",
                "m=video 55002 RTP/AVP 96",
                "a=rtpmap:96 H264/90000",
                ""
            ])
            sdp = parse_sdp(str_sdp)
            #self.failUnless(sdp.audio is not None)
            #self.failUnless(sdp.video is not None)

            new_str_sdp = str(sdp)
            compare_line_by_line(str_sdp.splitlines(), new_str_sdp.splitlines())
            print str(sdp) == str_sdp

    unittest.main()
