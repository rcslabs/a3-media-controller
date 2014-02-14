#!/usr/bin/env python
"""

"""


#from a3.media.payload_type_reserver import PayloadTypeReserver
import raw.sdp
import group
from raw.entity import NetType, AddrType
from a3.media import MediaType
from .media_description import MediaDescription


import itertools


class SessionDescription(object):
    def __init__(self, raw_sdp=None):
        assert raw_sdp is None or type(raw_sdp) is raw.sdp.Sdp
        #self.__pt_reserver = PayloadTypeReserver()
        self.__raw_sdp = raw_sdp if raw_sdp is not None else raw.sdp.Sdp()
        self.__media_descriptions = [MediaDescription(m, self) for m in self.__raw_sdp.medias]
        self.__group = group.Group(self)

    def __str__(self):
        return str(self.__raw_sdp)

    @property
    def raw_sdp(self):
        return self.__raw_sdp

    @property
    def rtp_codecs(self):
        return list(itertools.chain([media.rtp_codecs for media in self.__media_descriptions]))

    @property
    def host(self):
        if self.__raw_sdp.connection_data:
            return self.__raw_sdp.connection_data.connection_address
        else:
            return None

    @host.setter
    def host(self, host):
        assert host is None or type(host) is str
        if host is not None:
            self.__raw_sdp.connection_data = raw.entity.ConnectionData(NetType.IN, AddrType.IP4, host)
        else:
            self.__raw_sdp.connection_data = None

    @property
    def medias(self):
        return self.__media_descriptions

    def get_media(self, media_type):
        assert type(media_type) is MediaType
        for m in self.__media_descriptions:
            if m.media_type is media_type:
                return m
        return None

    def add_raw_media(self, raw_media):
        media = MediaDescription(raw_media, self)
        self.__media_descriptions.append(media)
        self.__raw_sdp.add_media(raw_media)
        self.__group.add_media(media)
        return media

    @property
    def audio(self):
        return self.get_media(MediaType.AUDIO)
    
    @property
    def video(self):
        return self.get_media(MediaType.VIDEO)

    @property
    def origin_value(self):
        return self.__raw_sdp.origin_value

    @property
    def session_name(self):
        return self.__raw_sdp.session_name.value

    @session_name.setter
    def session_name(self, session_name):
        assert type(session_name) is str
        self.__raw_sdp.session_name.value = session_name

    @property
    def group_semantics(self):
        return self.__group.semantics

    @group_semantics.setter
    def group_semantics(self, semantics):
        self.__group.semantics = semantics

    def get_remote_host(self):
        host = self.__raw_sdp.connection_data.connection_address
        return host

    #@property
    #def pt_reserver(self):
    #    return self.__pt_reserver


#
# Tests
#
if __name__ == "__main__":
    import unittest

    class SdpWrapperTest(unittest.TestCase):
        def test_init(self):
            sdp = SessionDescription()
            audio = sdp.add_media("audio")
            video = sdp.add_media("video")
            self.failUnlessEqual(sdp.audio, audio)
            self.failUnlessEqual(sdp.video, video)

    unittest.main()

    sdp = SessionDescription()


#   candidate-attribute   = "candidate" ":" foundation SP component-id SP
#                           transport SP
#                           priority SP
#                           connection-address SP     ;from RFC 4566
#                           port         ;port from RFC 4566
#                           SP cand-type
#                           [SP rel-addr]
#                           [SP rel-port]
#                           *(SP extension-att-name SP
#                                extension-att-value)
#
#   foundation            = 1*32ice-char
#   component-id          = 1*5DIGIT
#   transport             = "UDP" / transport-extension
#   transport-extension   = token              ; from RFC 3261
#   priority              = 1*10DIGIT
#   cand-type             = "typ" SP candidate-types
#   candidate-types       = "host" / "srflx" / "prflx" / "relay" / token
#   rel-addr              = "raddr" SP connection-address
#   rel-port              = "rport" SP port
#   extension-att-name    = byte-string    ;from RFC 4566
#   extension-att-value   = byte-string
#   ice-char              = ALPHA / DIGIT / "+" / "/"


#For media streams
#      based on RTP, candidates for the actual RTP media MUST have a
#      component ID of 1, and candidates for RTCP MUST have a component
#      ID of 2.



#C->S: {"sdp":"
#v=0
#o=- 830320942 2 IN IP4 127.0.0.1
#s=-
#t=0 0
#a=group:BUNDLE audio video
#a=msid-semantic: WMS vn7yXi1OjJ6CVPavCTtJeGE1ohpsu8CuQ4y3
#m=audio 1 RTP/SAVPF 111 103 104 0 8 126
#c=IN IP4 0.0.0.0
#a=rtcp:1 IN IP4 0.0.0.0
#a=ice-ufrag:lReNzue8HxnC/VXP
#a=ice-pwd:dtyy51IyYkn1mF6z0HkJ6w67
#a=ice-options:google-ice
#a=fingerprint:sha-256 14:31:FB:23:F9:A6:31:FF:D1:8E:1D:EE:BE:34:3B:D0:CC:37:77:61:60:F1:C0:7F:9C:3B:1E:F5:5E:33:72:9A
#a=sendrecv
#a=mid:audio
#a=rtcp-mux
#a=crypto:1 AES_CM_128_HMAC_SHA1_80 inline:hEYMCUOo8YzHpgMz4InXf3gaLwK2XE7aQ65W70rQ
#a=rtpmap:103 ISAC/16000
#a=rtpmap:104 ISAC/32000
#a=rtpmap:111 opus/48000/2
#a=fmtp:111 minptime=10
#a=rtpmap:0 PCMU/8000
#a=rtpmap:8 PCMA/8000
#a=rtpmap:126 telephone-event/8000
#a=maxptime:60
#a=ssrc:163910515 cname:yGUAz7Kn04WIjbiD
#a=ssrc:163910515 msid:vn7yXi1OjJ6CVPavCTtJeGE1ohpsu8CuQ4y3 vn7yXi1OjJ6CVPavCTtJeGE1ohpsu8CuQ4y3a0
#a=ssrc:163910515 mslabel:vn7yXi1OjJ6CVPavCTtJeGE1ohpsu8CuQ4y3
#a=ssrc:163910515 label:vn7yXi1OjJ6CVPavCTtJeGE1ohpsu8CuQ4y3a0
#m=video 1 RTP/SAVPF 100 116 117
#c=IN IP4 0.0.0.0
#a=rtcp:1 IN IP4 0.0.0.0
#a=ice-ufrag:lReNzue8HxnC/VXP
#a=ice-pwd:dtyy51IyYkn1mF6z0HkJ6w67
#a=ice-options:google-ice
#a=fingerprint:sha-256 14:31:FB:23:F9:A6:31:FF:D1:8E:1D:EE:BE:34:3B:D0:CC:37:77:61:60:F1:C0:7F:9C:3B:1E:F5:5E:33:72:9A
#a=sendrecv
#a=mid:video
#a=rtcp-mux
#a=crypto:1 AES_CM_128_HMAC_SHA1_80 inline:hEYMCUOo8YzHpgMz4InXf3gaLwK2XE7aQ65W70rQ
#a=rtpmap:100 VP8/90000
#a=rtpmap:116 red/90000
#a=rtpmap:117 ulpfec/90000
#a=ssrc:2649854635 cname:yGUAz7Kn04WIjbiD
#a=ssrc:2649854635 msid:vn7yXi1OjJ6CVPavCTtJeGE1ohpsu8CuQ4y3 vn7yXi1OjJ6CVPavCTtJeGE1ohpsu8CuQ4y3v0
#a=ssrc:2649854635 mslabel:vn7yXi1OjJ6CVPavCTtJeGE1ohpsu8CuQ4y3
#a=ssrc:2649854635 label:vn7yXi1OjJ6CVPavCTtJeGE1ohpsu8CuQ4y3v0
#","type":"offer"





#                                                 foundation component-id  transport   priority   conn-addr      port  cand-type
#{"label":0,"id":"audio","candidate":"a=candidate:2896278100       1           udp     2113937151 192.168.1.36   65249 typ host    generation 0\r\n"}
#{"label":0,"id":"audio","candidate":"a=candidate:2896278100       2           udp     2113937151 192.168.1.36   65249 typ host    generation 0\r\n"}
#{"label":0,"id":"audio","candidate":"a=candidate:2699642755       1           udp     2113937151 192.168.197.1  65250 typ host    generation 0\r\n"}
#{"label":0,"id":"audio","candidate":"a=candidate:2699642755       2           udp     2113937151 192.168.197.1  65250 typ host    generation 0\r\n"}
#{"label":0,"id":"audio","candidate":"a=candidate:41517227         1           udp     2113937151 192.168.245.1  65251 typ host    generation 0\r\n"}
#{"label":0,"id":"audio","candidate":"a=candidate:41517227         2           udp     2113937151 192.168.245.1  65251 typ host    generation 0\r\n"}
#{"label":0,"id":"audio","candidate":"a=candidate:1512488832       1           udp     2113937151 169.254.167.30 65252 typ host    generation 0\r\n"}
#{"label":0,"id":"audio","candidate":"a=candidate:1512488832       2           udp     2113937151 169.254.167.30 65252 typ host    generation 0\r\n"}
#{"label":0,"id":"audio","candidate":"a=candidate:1521601408       1           udp     1845501695 194.8.172.178  65249 typ srflx raddr 192.168.1.36 rport 65249 generation 0\r\n"}
#{"label":0,"id":"audio","candidate":"a=candidate:1521601408       2           udp     1845501695 194.8.172.178  65249 typ srflx raddr 192.168.1.36 rport 65249 generation 0\r\n"}
#
#{"label":0,"id":"audio","candidate":"a=candidate:4233069003       1           tcp     1509957375 192.168.56.1   51173 typ host generation 0\r\n"}
#{"label":0,"id":"audio","candidate":"a=candidate:3793899172       1           tcp     1509957375 192.168.1.36   51174 typ host generation 0\r\n"}
#{"label":0,"id":"audio","candidate":"a=candidate:3999972211       1           tcp     1509957375 192.168.197.1  51175 typ host generation 0\r\n"}
#{"label":0,"id":"audio","candidate":"a=candidate:1291484251       1           tcp     1509957375 192.168.245.1  51176 typ host generation 0\r\n"}
#{"label":0,"id":"audio","candidate":"a=candidate:346375024        1           tcp     1509957375 169.254.167.30 51177 typ host generation 0\r\n"}




