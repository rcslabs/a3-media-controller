#!/usr/bin/env python


import raw.media.entity
import random
import base64
import os


class MediaStreamTrack(object):
    def __init__(self, media_type, track_id, label=None):
        assert type(media_type) is raw.media.entity.MediaTypeValue
        assert type(track_id) is int
        assert label is None or type(label) is str
        self.__media_type = media_type
        self.__track_id = track_id
        self.__label = label

    @property
    def media_type(self):
        return self.__media_type

    @property
    def track_id(self):
        return self.__track_id

    @property
    def label(self):
        return self.__label if self.__label is not None else self.__track_id


class MediaStream(object):
    def __init__(self, stream_id, label=None):
        assert type(stream_id) is str
        assert label is None or type(label) is str
        self.__tracks = []
        self.__stream_id = stream_id
        self.__label = label

    @property
    def stream_id(self):
        return self.__stream_id

    @property
    def label(self):
        return self.__label if self.__label is not None else self.__stream_id

    @property
    def tracks(self):
        return self.__tracks

    @property
    def audio_tracks(self):
        return filter(lambda track: track.media_type == raw.media.entity.MediaType.AUDIO, self.__tracks)

    @property
    def video_tracks(self):
        return filter(lambda track: track.media_type == raw.media.entity.MediaType.VIDEO, self.__tracks)

    def add_track(self, media_stream_track):
        assert type(media_stream_track) is MediaStreamTrack
        self.__tracks.append(media_stream_track)


class StreamInfo(object):
    def __init__(self, ssrc, cname, media_stream):
        assert type(ssrc) is long
        assert type(cname) is str
        assert type(media_stream) is MediaStream
        self.__ssrc = ssrc
        self.__cname = cname
        self.__media_stream = media_stream

    @property
    def ssrc(self):
        return self.__ssrc

    @property
    def cname(self):
        return self.__cname


def generate_stream_info(vv, ssrc=None, cname=None):
    assert len(vv) == 2 and type(vv[0]) is bool and type(vv[1]) is bool
    assert ssrc is None or type(ssrc) is long
    if ssrc is None:
        ssrc = long(random.getrandbits(32))
    if cname is None:
        cname = base64.b64encode(os.urandom(12))
    stream_id = base64.b64encode(os.urandom(27))
    media_stream = MediaStream(stream_id)
    if vv[0]:
        media_stream.add_track(MediaStreamTrack(raw.media.entity.MediaType.AUDIO, stream_id + "a0"))
    if vv[1]:
        media_stream.add_track(MediaStreamTrack(raw.media.entity.MediaType.VIDEO, stream_id + "v0"))
    stream_info = StreamInfo(ssrc, cname, media_stream)
    return stream_info

