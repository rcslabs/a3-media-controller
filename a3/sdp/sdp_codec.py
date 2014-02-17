#!/usr/bin/env python
"""
TODO: replace SdpCodec class with RtpCodec from a3.media
replace SdpCodecCollection with list

"""

import logging
import itertools

from raw.attribute import Attribute, AttributeCollection, RtpmapValue
import raw.media

from a3.logging import LOG
from a3.media import Codec, RtpCodec, MediaType
#from a3.media.payload_type_reserver import PayloadTypeReserver, PayloadTypeReserverError, KNOWN_PT_CODECS
from error import SemanticError

from a3.media.payload_type_reserver import KNOWN_RTP_CODECS, DYNAMIC_PT


class UnknownCodecError(Exception):
    def __init__(self, payload_type):
        assert type(payload_type) is int
        self.value = payload_type

    def __str__(self):
        return str(self.value)


def create_codec_from_attributes(media_type, payload_type, attributes):
    """
    TODO: use imageattr and fmtp to create Codec
    """
    assert type(media_type) is MediaType
    assert type(payload_type) is int
    assert type(attributes) is AttributeCollection

    pt_filter = lambda attr: attr.value.payload_type == payload_type
    rtpmaps = filter(pt_filter, attributes.get("rtpmap"))
    fmtps = filter(pt_filter, attributes.get("fmtp"))
    imageattrs = filter(pt_filter, attributes.get("imageattr"))

    if len(rtpmaps) > 1 or len(fmtps) > 1 or len(imageattrs) > 1:
        raise SemanticError("Too many sdp entries for one media " + repr(payload_type))

    rtpmap =  rtpmaps[0] if len(rtpmaps) == 1 else None
    fmtp = fmtps[0] if len(fmtps) == 1 else None
    imageattr = imageattrs[0] if len(imageattrs) == 1 else None

    #
    # in case of codec does not have rtpmap entry and its payload type is unknown
    #
    if rtpmap is not None:
        rtp_codec = RtpCodec(Codec(media_type,
                                   rtpmap.value.encoding_name,
                                   rtpmap.value.clock_rate,
                                   rtpmap.value.channels or 1),
                             payload_type)
    else:
        known_codecs = [rtp_codec for rtp_codec in KNOWN_RTP_CODECS if rtp_codec.payload_type == payload_type]
        if len(known_codecs) == 0:
            # In case of no entry in sdp there should be default value of payload type
            # in RTPMAP defaults
            raise UnknownCodecError(payload_type)

        assert len(known_codecs) == 1
        rtp_codec = known_codecs[0]

    return rtp_codec


class SdpCodecCollection(object):
    def __init__(self, raw_media):
        """

        :param raw_media: raw media object
        :param pt_reserver: payload type reserver
        """
        assert type(raw_media) is raw.media.Media
        self.__raw_media = raw_media
        self.__rtp_codecs = []

        for payload_type in self.payload_types:
            try:
                rtp_codec = create_codec_from_attributes(raw_media.media_type,
                                                         payload_type,
                                                         self.__raw_media.attributes)
                self.__rtp_codecs.append(rtp_codec)
            except UnknownCodecError as e:
                LOG.warn("Unknown codec with payload type %d", e.value)
            #except PayloadTypeReserverError as e:
            #    LOG.warn("Error while reserving payload for codec: %s", str(e))

        # TODO: check extra rtpmap, fmtp and imageattr attributes
        # There might be fmtp:*

    @property
    def payload_types(self):
        return self.__raw_media.media_description.fmt

    #@property
    #def pt_codec_collection(self):
    #    return self.__pt_reserver.pt_codec_collection.filter_by_media_type(self.__raw_media.media_type)

    def __len__(self):
        return len(self.__rtp_codecs)

    def __nonzero__(self):
        return len(self.__rtp_codecs) != 0

    def __bool__(self):
        return self.__nonzero__()

    def __iter__(self):
        return self.__rtp_codecs.__iter__()

    def __getitem__(self, key):
        return self.__rtp_codecs[key]

    @property
    def rtp_codecs(self):
        return self.__rtp_codecs

    #@property
    #def attributes(self):
    #    return list(itertools.chain.from_iterable(map(lambda codec: codec.attributes, self.__rtp_codecs)))

    def add_codec(self, codec):
        """

        :param codec: Codec
        """
        assert type(codec) is Codec
        known_codecs = [rtp_codec for rtp_codec in KNOWN_RTP_CODECS if rtp_codec.base_codec == codec]
        if len(known_codecs):
            rtp_codec = known_codecs[0].clone()
        else:
            payload_types = list(DYNAMIC_PT)
            for rtp_codec in self.__rtp_codecs:
                if rtp_codec.payload_type in payload_types:
                    payload_types.remove(rtp_codec.payload_type)

            # TODO: throw exception
            assert len(payload_types) > 0
            payload_type = payload_types[0]

            rtp_codec = RtpCodec(codec, payload_type)
            rtpmap = Attribute("rtpmap", RtpmapValue(payload_type=payload_type,
                                                     encoding_name=codec.encoding_name,
                                                     clock_rate=codec.clock_rate,
                                                     channels=codec.channels if codec.channels != 1 else None))
            # add rtpmap attribute
            self.__raw_media.attributes.append(rtpmap)

        # add payload_type
        self.__rtp_codecs.append(rtp_codec)
        self.payload_types.append(rtp_codec.payload_type)


if __name__ == "__main__":
    import unittest
    FORMAT = '%(asctime)-15s %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.DEBUG)

    PT_MAP = [8, 96, 97, 98]

    ATTRIBUTES = [
        "rtpmap:96 VP8/90000",
        "fmtp:96 1-16",
        "imageattr:96 send [x=320,y=240]",
        "rtpmap:97 H263/90000/2",
        "rtpmap:98 PCMU/8000",
        "fmtp:98 annexb=no",
        "ice-ufrag:username",
        "ice-pwd:password",
    ]

    def get_raw_media():
        media = raw.media.Media()
        media.media_description.fmt = PT_MAP[:]
        for s in ATTRIBUTES:
            media.attributes.append(raw.attribute.Attribute.from_string(s))
        return media

    class CodecTest(unittest.TestCase):
        def test_init(self):
            rtpmap96 = raw.attribute.Attribute("rtpmap", raw.attribute.RtpmapValue(96, "VP8", 90000, 1))
            fmtp96 = raw.attribute.Attribute("fmtp", raw.attribute.FmtpValue(96, "0-16"))
            imageattr96 = raw.attribute.Attribute("imageattr", raw.attribute.ImageattrValue(96, "[x=320,y=200]"))
            attributes = raw.attribute.AttributeCollection([rtpmap96, fmtp96, imageattr96])
            c1 = SdpCodec.from_attributes(MediaType.VIDEO, 96, attributes)
            self.failUnlessEqual(c1.payload_type, 96)
            self.failUnlessEqual(c1.info.encoding_name, "VP8")
            self.failUnlessEqual(c1.info.clock_rate, 90000)
            self.failUnlessEqual(c1.info.channels, 1)

            fmtp97 = raw.attribute.Attribute("fmtp", raw.attribute.FmtpValue(97, "0-16"))
            attributes.append(fmtp97)
            self.failUnlessRaises(UnknownCodecError, SdpCodec.from_attributes, 97, attributes)

    class CodecCollectionTest(unittest.TestCase):
        def test_init(self):
            raw_media = get_raw_media()
            codecs = SdpCodecCollection(raw_media)
            self.failUnlessEqual(len(codecs), 4)
            self.failUnlessEqual(codecs[0].info.encoding_name, "PCMA")
            self.failUnlessEqual(codecs[1].info.encoding_name, "VP8")
            self.failUnlessEqual(codecs[2].info.encoding_name, "H263")
            self.failUnlessEqual(codecs[3].info.encoding_name, "PCMU")
            self.failUnlessEqual(codecs[3].fmtp_parameters, "annexb=no")

            l1 = codecs.infos
            l2 = [Codec("PCMA", 8000),
                  Codec("VP8", 90000),
                  Codec("H263", 90000),
                  Codec("PCMU", 8000)]
            self.failUnlessEqual(l1, l2)

        def test_add(self):
            raw_media = get_raw_media()
            codecs = SdpCodecCollection(raw_media)
            codecs.add(Codec("VP9", 90000))
            self.failUnlessEqual(len(codecs), 5)
            attr = raw_media.attributes[6]
            self.failUnlessEqual(attr.name, "rtpmap")
            self.failUnlessEqual(attr.value.payload_type, 99)
            self.failUnlessEqual(attr.value.encoding_name, "VP9")

    unittest.main()
