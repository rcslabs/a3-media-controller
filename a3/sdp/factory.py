#!/usr/bin/env python


from a3.logging import LOG
import capabilities
from session_description import SessionDescription
import raw.media
from raw.entity import MediaDescriptionProto, ConnectionData, NetType, AddrType
from raw.attribute import GroupSemantics
from a3.media import MediaType
from .direction import SdpDirection
from raw.parser import parse_sdp

import collections


class Factory(object):

    @classmethod
    def create_offer(cls, cc, vv, supported_codecs):
        assert type(cc) is capabilities.Cc
        assert type(vv) is capabilities.Vv
        assert isinstance(supported_codecs, collections.Iterable)
        sdp = SessionDescription()

        if cc.bundle:
            sdp.group_semantics = GroupSemantics.BUNDLE

        for media_type in vv.media_types:
            assert media_type in [MediaType.AUDIO, MediaType.VIDEO]

            codecs = [codec for codec in cc.get_codecs(media_type) if codec in supported_codecs]
            LOG.debug("Cc: Creating media description (%s) based on codecs: %s",
                      str(media_type),
                      ",".join([str(codec) for codec in codecs]))

            raw_media = raw.media.Media(media_type=media_type)
            media = sdp.add_raw_media(raw_media)

            if cc.rtcp_mux:
                media.rtcp_mux = True

            for codec in codecs:
                media.add_codec(codec)

            media.raw_media.media_description.proto = cc.profile

            if cc.profile == MediaDescriptionProto.RTP_SAVPF:
                media.crypto.generate_AES_CM_128_HMAC_SHA1_80()

            if cc.ssrc_required:
                media.direction = SdpDirection.RECV_ONLY

            if cc.ice:
                media.raw_media.connection_data = ConnectionData(NetType.IN,
                                                                 AddrType.IP4,
                                                                 "0.0.0.0")
                media.rtcp.port = 1
                media.rtcp.connection_address = "0.0.0.0"
                media.ice.generate_google_ice()

            if media_type is MediaType.AUDIO:
                #
                # some hacks
                #
                #media.packet_time = 20
                #media.silence_supp_enable = False
                #media.codecs.add(Codec("telephone-event", 8000))
                pass
                # fmtp:101 0-15

        #if self._ice:
        #    #sdp.host = None                                          # ??? ERROR???
        #    ice_ufrag, ice_pwd = gen_ice_pair()
        #    sdp.set_ice(ice_ufrag, ice_pwd, "google-ice")
        #else:
        #    sdp.host = host

        # http://code.google.com/p/webrtc/issues/detail?id=757
        # As per the latest draft when you use BUNDLE in offer/answer than rtcp-mux attribute must be specified.
        # In your case you are using BUNDLE in answer without rtcp-mux. Please refer to section 6.1 in the below draft.
        #http://datatracker.ietf.org/doc/draft-ietf-mmusic-sdp-bundle-negotiation/?include_text=1
        #
        #if cc.rtcp_mux:
        #    sdp.group_bundle()

        return sdp

        #def gen_ssrc(self):
        #    if self.ssrc is None:
        #        self.ssrc = str(random.getrandbits(32))

    @classmethod
    def create_from_string(cls, string):
        assert type(string) is str
        raw_sdp = parse_sdp(string)
        sdp = SessionDescription(raw_sdp)
        return sdp


if __name__ == "__main__":

    import unittest

    class TestFactory(unittest.TestCase):
        def test_offer_default_audio(self):
            sdp = Factory.create_offer(capabilities.Cc({}), capabilities.Vv([True, False]))
            self.failUnlessEqual(str(sdp).split("\r\n"), ["v=0",
                                                          "o=- 0 0 IN IP4 127.0.0.1",
                                                          "s=Session SIP/SDP",
                                                          "t=0 0",
                                                          "m=audio 0 RTP/AVP 8",
                                                          "a=rtpmap:8 PCMA/8000",
                                                          ""])

        def test_offer_chrome(self):
            cc = capabilities.Cc({
                "profile": "RTP/SAVPF",
                "ice": True,
                "bundle": True,
                "ssrcRequired": True,
                "rtcpMux": True,
                "audio": ["PCMA/8000", "PCMU/8000"],
                "video": ["VP8/90000"]
            })
            vv = capabilities.Vv([True, True])
            sdp = Factory.create_offer(cc, vv)
            sdp.session_name = "-"
            # make some fixes to SDP
            print "2) sdp=", str(sdp)
            self.failUnlessEqual(str(sdp).split("\r\n"), [
                "v=0",
                "o=- 0 0 IN IP4 127.0.0.1",
                "s=-",
                "t=0 0",
                "a=group:BUNDLE audio video",
                "m=audio 0 RTP/SAVPF 8 0",
                "c=IN IP4 0.0.0.0",
                "a=mid:audio",
                "a=rtcp:1 IN IP4 0.0.0.0",
                "a=ice-ufrag:9wMh/Gc6fgJBzvzQ",
                "a=ice-pwd:4I4SozPeoRtm9C58OF8M/deY",
                "a=ice-options:google-ice",
                "a=sendrecv",
                "a=rtcp-mux",
                "a=crypto:1 AES_CM_128_HMAC_SHA1_80 inline:JyWcGXs7j0U5aWAj8RlUdSwWkBRtmbvg3njMO1FB",
                "a=rtpmap:103 ISAC/16000",
                "a=rtpmap:104 ISAC/32000",
                "a=rtpmap:0 PCMU/8000",
                "a=rtpmap:8 PCMA/8000",
                "a=rtpmap:106 CN/32000",
                "a=rtpmap:105 CN/16000",
                "a=rtpmap:13 CN/8000",
                "a=rtpmap:126 telephone-event/8000",
                "a=ssrc:1635880669 cname:ZXVf3drwG3fT+Wh5",
                "a=ssrc:1635880669 mslabel:cLFXFpfLOP31s7D1A9on2I2rAvhTKqGSZEWr",
                "a=ssrc:1635880669 label:cLFXFpfLOP31s7D1A9on2I2rAvhTKqGSZEWr00",
                "m=video 1 RTP/SAVPF 100 101 102",
                "c=IN IP4 0.0.0.0",
                "a=rtcp:1 IN IP4 0.0.0.0",
                "a=ice-ufrag:9wMh/Gc6fgJBzvzQ",
                "a=ice-pwd:4I4SozPeoRtm9C58OF8M/deY",
                "a=ice-options:google-ice",
                "a=sendrecv",
                "a=mid:video",
                "a=rtcp-mux",
                "a=crypto:1 AES_CM_128_HMAC_SHA1_80 inline:JyWcGXs7j0U5aWAj8RlUdSwWkBRtmbvg3njMO1FB",
                "a=rtpmap:100 VP8/90000",
                "a=rtpmap:101 red/90000",
                "a=rtpmap:102 ulpfec/90000",
                "a=ssrc:1563041388 cname:ZXVf3drwG3fT+Wh5",
                "a=ssrc:1563041388 mslabel:cLFXFpfLOP31s7D1A9on2I2rAvhTKqGSZEWr",
                "a=ssrc:1563041388 label:cLFXFpfLOP31s7D1A9on2I2rAvhTKqGSZEWr10"])

    unittest.main()

