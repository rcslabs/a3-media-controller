#!/usr/bin/env python
"""
Room class


"""


from a3.logging import LOG
from a3.media import MediaType
from media_room import MediaRoom
from point import Point
from a3.transcoding._base import ITranscodingFactory


class Room(object):
    def __init__(self, room_id, transcoding_factory):
        assert type(room_id) is str
        assert isinstance(transcoding_factory, ITranscodingFactory)
        self.__room_id = room_id
        self.__transcoding_factory = transcoding_factory
        self.__points = []
        self.__audio_room = None
        self.__video_room = None

    @property
    def room_id(self):
        return self.__room_id

    def join(self, point):
        # we have PointController here
        # TODO: create RoomController
        point = point.point
        assert isinstance(point, Point)
        if point in self.__points:
            LOG.warning("Attempt to join room %s more than once", self.__room_id)
            return

        self.__points.append(point)

        if point.audio_point:
            self.__get_audio_room().join(point.audio_point)

        if point.video_point:
            self.__get_video_room().join(point.video_point)

    def unjoin(self, point):
        # we have PointController here
        # TODO: create RoomController
        point = point.point
        assert isinstance(point, Point)
        if point.audio_point:
            self.__audio_room.unjoin(point.audio_point)

        if point.video_point:
            self.__video_room.unjoin(point.video_point)

        self.__points.remove(point)

        #for mp in self.__points:
        #    mp.commit_local_sdp_change()

    @property
    def points_count(self):
        return len(self.__points)

    def stop(self):
        while len(self.__points):
            self.unjoin(self.__points[0])

    def __get_audio_room(self):
        if self.__audio_room is None:
            self.__audio_room = MediaRoom(MediaType.AUDIO, self.__transcoding_factory)
        return self.__audio_room

    def __get_video_room(self):
        if self.__video_room is None:
            self.__video_room = MediaRoom(MediaType.VIDEO, self.__transcoding_factory)
        return self.__video_room

    def dispose(self):
        """
        TODO: implement clean-up
        """