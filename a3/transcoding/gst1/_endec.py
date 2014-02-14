#! /usr/bin/env python
"""
Gstreamer-1 encoders/decoders
"""

__author__ = 'RCSLabs'


from ...media import CODEC, RtpCodec, Codec
from .gst_elements import *


RTP_CAPS = {
    # audio
    CODEC.PCMA: "application/x-rtp,media=(string)audio,encoding-name=(string)PCMA,clock-rate=8000",

    #video
    CODEC.H264: "application/x-rtp,media=(string)video,encoding-name=(string)H264,clock-rate=90000,rtcp-fb-nack-pli=(int)1,rtcp-fb-ccm-fir=(int)1",
    CODEC.VP8: "application/x-rtp,media=(string)video,encoding-name=(string)VP8-DRAFT-IETF-01,clock-rate=90000,rtcp-fb-nack-pli=(int)1,rtcp-fb-ccm-fir=(int)1",
    CODEC.H263_1998: "application/x-rtp,media=(string)video,encoding-name=(string)H263-1998,clock-rate=90000,rtcp-fb-nack-pli=(int)1,rtcp-fb-ccm-fir=(int)1"
}


# def create_depay_decoder(codec):
#     assert type(codec) is RtpCodec
#     decoder = None
#     if codec == CODEC.PCMA:
#         decoder = PCMADepayDecoder()
#     elif codec == CODEC.H264:
#         decoder = H264DepayDecoder()
#     elif codec == CODEC.VP8:
#         decoder = VP8DepayDecoder()
#     elif codec == CODEC.H263_1998:
#         decoder = H263_1998DepayDecoder()
#     else:
#         # TODO: throw exception
#         assert not ("Known media for decoding " + codec.encoding_name)
#     return decoder
#
#
# def create_encoder_pay(rtp_codec):
#     assert type(rtp_codec) is RtpCodec
#     encoder = None
#     if rtp_codec.codec == CODEC.PCMA:
#         encoder = PCMAEncoderPay(1111L, rtp_codec.payload_type)
#     elif rtp_codec.codec == CODEC.H264:
#         encoder = H264EncoderPay(2222L, rtp_codec.payload_type)
#     elif rtp_codec.codec == CODEC.VP8:
#         encoder = VP8EncoderPay(2222L, rtp_codec.payload_type)
#     elif rtp_codec.codec == CODEC.H263_1998:
#         encoder = H263_1998EncoderPay(2222L, rtp_codec.payload_type)
#     else:
#         assert not ("Known media for encoding " + rtp_codec.encoding_name)
#     return encoder


def create_depay(rtp_codec):
    assert type(rtp_codec) is RtpCodec
    depay = None
    if rtp_codec == CODEC.PCMA:
        depay = PCMADepay()
    elif rtp_codec == CODEC.H264:
        depay = H264Depay()
    elif rtp_codec == CODEC.VP8:
        depay = VP8Depay()
    elif rtp_codec == CODEC.H263_1998:
        depay = H263_1998Depay()
    else:
        # TODO: throw exception
        assert not ("Known media for decoding " + rtp_codec.encoding_name)
    return depay


def create_pay(rtp_codec):
    """
    creates decoder Gst element
    :param rtp_codec: a codec to create decoder
    :type rtp_codec: RtpCodec
    :rtype : GstElement
    :return:
    """
    assert type(rtp_codec) is RtpCodec
    pay = None
    if rtp_codec == CODEC.PCMA:
        pay = PCMAPay(1111L, rtp_codec.payload_type)
    elif rtp_codec == CODEC.H264:
        pay = H264Pay(2222L, rtp_codec.payload_type)
    elif rtp_codec == CODEC.VP8:
        pay = VP8Pay(2222L, rtp_codec.payload_type)
    elif rtp_codec == CODEC.H263_1998:
        pay = H263_1998Pay(2222L, rtp_codec.payload_type)
    else:
        # TODO: throw exception
        assert not ("Known media for decoding " + rtp_codec.encoding_name)
    return pay


def create_decoder(codec):
    """
    creates decoder Gst element
    :param codec: a codec to create decoder
    :type codec: Codec
    :rtype : Decoder
    :return:
    """
    assert type(codec) is Codec
    depay = None
    if codec == CODEC.PCMA:
        depay = PCMADecoder()
    elif codec == CODEC.H264:
        depay = H264Decoder()
    elif codec == CODEC.VP8:
        depay = VP8Decoder()
    elif codec == CODEC.H263_1998:
        depay = H263_1998Decoder()
    else:
        # TODO: throw exception
        assert not ("Known media for decoding " + codec.encoding_name)
    return depay


def create_encoder(codec):
    """
    creates encoder Gst element
    :param codec: a codec to create decoder
    :type codec: Codec
    :rtype : Encoder
    :return:
    """
    assert type(codec) is Codec
    encoder = None
    if codec == CODEC.PCMA:
        encoder = PCMAEncoder()
    elif codec == CODEC.H264:
        encoder = H264Encoder()
    elif codec == CODEC.VP8:
        encoder = VP8Encoder()
    elif codec == CODEC.H263_1998:
        encoder = H263_1998Encoder()
    else:
        # TODO: throw exception
        assert not ("Known media for decoding " + codec.encoding_name)
    return encoder
