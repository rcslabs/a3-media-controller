#!/usr/bin/env python
"""
Manager
"""

__author__ = 'RCSLabs'


from ..logging import LOG
from ..config import IConfig
from ..transcoding._base import ITranscodingFactory
from .room import Room
from .point_controller import PointController, Event as PointEvent


class ManagerError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Manager(object):
    def __init__(self, config, transcoding_factory):
        assert isinstance(config, IConfig)
        assert isinstance(transcoding_factory, ITranscodingFactory)
        self.__config = config
        self.__transcoding_factory = transcoding_factory

        self.__points = dict()
        self.__rooms = dict()

    #
    # public
    #
    def get_point(self, point_id):
        return self.__get_point(point_id)

    def create_point(self, **kwargs):
        point_id = str(kwargs["point_id"])
        LOG.info("Creating point " + repr(point_id))
        point = self.get_point(point_id)
        if point is not None:
            raise ManagerError("Attempt to add existing media point")

        point = PointController(**kwargs)
        self.__points[point_id] = point
        return point

    def remove_room(self, room_id):
        assert type(room_id) is str
        room = self.__get_room(room_id)
        if room:
            self.__remove_room(room)

    def remove_point(self, point_id):
        point = self.get_point(point_id)
        if point is None:
            raise ManagerError("Attempt to remove nonexisting point")

        room = self.get_room_for_point(point)
        if room is not None:
            room.unjoin(point)
            self.unjoin_point(point)
            if room.points_count == 0:
                self.remove_room(room)

        point.event(PointEvent.REMOVE)
        del self.__points[point.point_id]

    def join_room(self, point_id, room_id):
        point = self.__get_point(point_id)
        if point is None:
            raise ManagerError("Attempt to join_room with unexisting point")

        room = self.get_room(room_id)
        current_room = self.get_room_for_point(point)
        if current_room is not None and current_room is not room:
            current_room.unjoin(point)
            self.unjoin(point_id)
            current_room = None

        if current_room != room:
            point.room = room
            room.join(point)
        else:
            raise ManagerError("Attempt to join point to room where point is already")

    def unjoin(self, point_id):
        point = self.__get_point(point_id)
        if point is None:
            raise ManagerError("Attempt to unjoin with unexisting point")

        room = self.get_room_for_point(point)
        if room is None:
            raise ManagerError("Attempt to unjoin point which is without room")

        self.__unjoin(point)

    #
    # private
    #
    def get_room_for_point(self, point_controller):
        assert type(point_controller) is PointController
        return point_controller.room

    def get_room(self, room_id):
        assert type(room_id) is str
        if room_id in self.__rooms:
            return self.__rooms[room_id]
        room = Room(room_id, self.__transcoding_factory)
        self.__rooms[room_id] = room
        return room

    def __unjoin(self, point):
        assert type(point) is PointController
        room = self.get_room_for_point(point)
        if room:
            LOG.debug("Manager. Room[%s] unjoin point [%s]", room.room_id, point.point_id)
            room.unjoin(point)
            point.room = None
            if room.points_count == 0:
                self.__remove_room(room)

    def __remove_room(self, room):
        assert type(room) is Room and room.points_count == 0
        LOG.debug("Manager. remove room[%s]", room.room_id)
        room.stop()
        room.dispose()
        del self.__rooms[room.room_id]

    #
    # TODO: remove
    #
    def on_timer(self):
        for point in self.__points.values():
            point.event(PointEvent.TIMER)

    def __get_point(self, point_id):
        assert type(point_id) is str
        return self.__points[point_id] if point_id in self.__points else None

    def __get_room(self, room_id):
        assert type(room_id) is str
        return self.__rooms[room_id] if room_id in self.__rooms else None

    def bind_point_to_room(self, point_controller, room):
        assert type(point_controller) is PointController
        point_controller.room = room

