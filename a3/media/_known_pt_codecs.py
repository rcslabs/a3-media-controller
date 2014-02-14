#!/usr/bin/env python
"""

known codecs associated with their standard payload types
http://en.wikipedia.org/wiki/RTP_audio_video_profile

TODO: move it to a3.session_description

"""

__author__ = 'RCSLabs'


from ._codec import AudioCodec, VideoCodec, RtpCodec


KNOWN_RTP_CODECS = [
    RtpCodec(AudioCodec("PCMU",  8000,  1),  0),
    #RtpCodec(AudioCodec("GSM",   8000,  1),  3),
    #RtpCodec(AudioCodec("G723",  8000,  1),  4),
    #RtpCodec(AudioCodec("DVI4",  8000,  1),  5),
    #RtpCodec(AudioCodec("DVI4",  16000, 1),  6),
    #RtpCodec(AudioCodec("LPC",   8000,  1),  7),
    RtpCodec(AudioCodec("PCMA",  8000,  1),  8),
    #RtpCodec(AudioCodec("G722",  8000,  1),  9),
    #RtpCodec(AudioCodec("L16",   44100, 2), 10),
    #RtpCodec(AudioCodec("L16",   44100, 1), 11),
    #RtpCodec(AudioCodec("QCELP", 8000,  1), 12),
    #RtpCodec(AudioCodec("CN",    8000,  1), 13),
    #RtpCodec(AudioCodec("MPA",   90000, 1), 14),
    #RtpCodec(AudioCodec("G728",  8000,  1), 15),
    #RtpCodec(AudioCodec("DVI4",  11025, 1), 16),
    #RtpCodec(AudioCodec("DVI4",  22050, 1), 17),
    #RtpCodec(AudioCodec("G729",  8000,  1), 18),

    #RtpCodec(VideoCodec("CELB",  90000, 1), 25),
    #RtpCodec(VideoCodec("JPEG",  90000, 1), 26),
    #RtpCodec(VideoCodec("NV",    90000, 1), 28),
    #RtpCodec(VideoCodec("H261",  90000, 1), 31),
    #RtpCodec(VideoCodec("MPV",   90000, 1), 32),
    #RtpCodec(Codec(!!! MediaType.AUDIO  / MediaType.VIDEO, "MP2T",  90000, 1), 33),
    RtpCodec(VideoCodec("H263",  90000, 1), 34),
    #
    #RtpCodec(101: AudioCodec("telephone-event", 8000, 1)
]
