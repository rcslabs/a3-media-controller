#!/usr/bin/env python
"""
Capabilities
Cc - codecs capabilities
Vv - voice-video

Cc = {
    profile : "RTP/AVP" | "RTP/SAVPF"
    ice : true | false
    ssrcRequired: true | false
    rtcpMux: true | false
    audio: [ media-list ],
    video: [ media-list ]
}
"""


import raw
import raw.entity
from a3.media import Codec, CODEC, MediaType
from error import SemanticError
from raw.sdp import ParseError


import re


DEFAULT_PROFILE = raw.entity.MediaDescriptionProto.RTP_AVP
#DEFAULT_AUDIO_CODECS = [CODEC.PCMA]
#DEFAULT_VIDEO_CODECS = [CODEC.H264]


class Cc(object):
    def __init__(self, cc_object):
        if "profile" in cc_object:
            try:
                self.__profile = raw.entity.MediaDescriptionProto.from_string(str(cc_object["profile"]))
            except ParseError:
                raise SemanticError("Error CC value profile " + repr(cc_object["profile"]))
        else:
            self.__profile = DEFAULT_PROFILE

        self.__ice = ("ice" in cc_object) and cc_object["ice"] is True
        self.__ssrc_required = ("ssrcRequired" in cc_object) and cc_object["ssrcRequired"] is True
        self.__bundle = ("bundle" in cc_object) and cc_object["bundle"] is True
        self.__rtcp_mux = ("rtcpMux" in cc_object) and cc_object["rtcpMux"] is True
        if "audio" in cc_object:
            self.__audio_codecs = [self.__parse_codec(str(str_codec), MediaType.AUDIO)
                                   for str_codec in cc_object["audio"]]
        if "video" in cc_object:
            self.__video_codecs = [self.__parse_codec(str(str_codec), MediaType.VIDEO)
                                   for str_codec in cc_object["video"]]

    def __parse_codec(self, string, media_type):
        """
        Parse string in serdes:
        encoding-name/clock-rate[/channels]
        """
        assert type(string) is str
        assert type(media_type) is MediaType
        g = re.match("^([\w\d\-]+)/(\d+)(?:/(\d+))?$", string)
        if not g:
            raise SemanticError("Error codec in Cc: " + repr(string))
        return Codec(encoding_name=g.group(1),
                     clock_rate=int(g.group(2)),
                     channels=(int(g.group(3)) if g.group(3) else 1),
                     media_type=media_type)

    @property
    def profile(self):
        return self.__profile

    @property
    def ice(self):
        return self.__ice

    @property
    def rtcp_mux(self):
        return self.__rtcp_mux

    @property
    def ssrc_required(self):
        return self.__ssrc_required

    @property
    def bundle(self):
        return self.__bundle

    @property
    def audio_codecs(self):
        return self.__audio_codecs

    @property
    def video_codecs(self):
        return self.__video_codecs

    def get_codecs(self, media_type):
        assert type(media_type) is MediaType
        return self.audio_codecs if media_type is MediaType.AUDIO \
            else self.video_codecs


class Vv(object):
    def __init__(self, vv_object):
        self.__audio = vv_object[0]
        self.__video = vv_object[1]

    @property
    def audio(self):
        return self.__audio

    @property
    def video(self):
        return self.__video

    @property
    def media_types(self):
        result = []
        if self.audio:
            result.append(MediaType.AUDIO)
        if self.video:
            result.append(MediaType.VIDEO)
        return result


if __name__ == "__main__":
    import unittest

    class CcTest(unittest.TestCase):
        def test_init(self):
            cc = Cc({
                "audio": ["PCMA/8000", "telephone-event/8000"],
                "video": ["H263/90000"]
            })
            self.failUnlessEqual(cc.profile, DEFAULT_PROFILE)
            self.failUnlessEqual(cc.ice, False)
            self.failUnlessEqual(cc.rtcp_mux, False)
            self.failUnlessEqual(cc.ssrc_required, False)
            self.failUnlessEqual(cc.audio_codecs, [Codec("PCMA", 8000, 2),
                                                   Codec("telephone-event", 8000)])
            self.failUnlessEqual(cc.video_codecs, [Codec("H263", 90000)])

        def test_init2(self):
            cc = Cc(dict(
                userAgent="Chrome",
                audio=["PCMA/8000", "NV/90000"],
                video=["H404/90000", "VP10/100000", "JPEG/8000", "H263/90000/4"],
                profile="RTP/SAVPF",
                rtcpMux=True,
                ice=True,
                ssrcRequired=True
            ))
            self.failUnlessEqual(cc.profile, raw.entity.MediaDescriptionProto.RTP_SAVPF)
            self.failUnlessEqual(cc.ice, True)
            self.failUnlessEqual(cc.rtcp_mux, True)
            self.failUnlessEqual(cc.ssrc_required, True)
            self.failUnlessEqual(cc.audio_codecs, [Codec("PCMA", 8000, 2),
                                                   Codec("NV", 90000)])
            self.failUnlessEqual(cc.video_codecs, [Codec("H404", 90000),
                                                   Codec("VP10", 100000),
                                                   Codec("JPEG", 8000),
                                                   Codec("H263", 90000, 4)])

        def test_init_fail(self):
            o = dict(audio=["WrongCodec"])
            self.failUnlessRaises(SemanticError, Cc, o)
            o = dict(audio=["RightCodec/8000"])
            Cc(o)
            o = dict(profile="BadProfile")
            self.failUnlessRaises(SemanticError, Cc, o)

    unittest.main()
