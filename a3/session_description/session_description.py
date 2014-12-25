#!/usr/bin/env python
"""
  session_description

"""


__author__ = 'esix'


from enum import Enum


Port = int


class IP(object):
    pass


class IP4(IP):
    def __init__(self, a, b, c, d):
        self.__a, self.__b, self.__c, self.__d = a, b, c, d


MediaType = Enum('MediaType', 'audio video')

MediaDirection = Enum('MediaFlow', 'sendrecv sendonly recvonly inactive')


class MediaDescription(object):
    def __init__(self, session_description):
        assert type(session_description) is SessionDescription
        self.__session_description = session_description
        self.__media_direction = MediaDirection.sendrecv

    @property
    def media_direction(self):
        return self.__media_direction

    @media_direction.setter
    def media_direction(self, media_direction):
        assert type(media_direction) is MediaDirection
        self.__media_direction = media_direction


class RtpMediaDescription(MediaDescription):
    pass


class RtmpMediaDescription(MediaDescription):
    pass


class SessionDescription(object):
    def __init__(self):
        self.__medias = []

    def create_rtp_media(self):
        media = RtpMediaDescription(self)
        self.__medias.append(media)
        return media

    def create_rtmp_media(self):
        media = RtmpMediaDescription(self)
        self.__medias.append(media)
        return media


