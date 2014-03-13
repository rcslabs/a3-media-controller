#!/usr/bin/env python
"""
Main media controller executable

preferred way to run is to execute command
# python -m media_controller


"""


import time

from a3 import messaging
from netpoint.balancer import Balancer
from a3.point.point_controller import PointController, PointControllerError, Event as PointEvent
from a3.logging import LOG
from a3.transcoding._base import ITranscodingFactory
from a3.config import IConfig
from a3.point.manager import Manager, ManagerError


class MessageType:
    CREATE_POINT = "CREATE_MEDIA_POINT"
    CREATE_POINT_OK = "CREATE_MEDIA_POINT_OK"
    CREATE_POINT_FAILED = "CREATE_MEDIA_POINT_FAILED"

    REMOVE_POINT = "REMOVE_MEDIA_POINT"
    REMOVE_POINT_OK = "REMOVE_MEDIA_POINT_OK"
    REMOVE_POINT_FAILED = "REMOVE_MEDIA_POINT_FAILED"

    CRITICAL_ERROR = "CRITICAL_ERROR"

    JOIN_ROOM = "JOIN_ROOM"
    UNJOIN_ROOM = "UNJOIN_ROOM"
    SDP_OFFER = "SDP_OFFER"
    SDP_ANSWER = "SDP_ANSWER"

    SEND_DTMF = "SEND_DTMF"


class MediaController(messaging.IMessageListener):

    def __init__(self, config, transcoding_factory):
        assert isinstance(config, IConfig)
        assert isinstance(transcoding_factory, ITranscodingFactory)
        self.__manager = Manager(config, transcoding_factory)
        self.__balancer = Balancer()
        self.__config = config
        self.__transcoding_factory = transcoding_factory

    def __get_point_by_id(self, point_id):
        return self.__manager.get_point(point_id)

    def get_room(self, room_id):
        return self.__manager.get_room(room_id)

    def on_timer(self):
        self.__manager.on_timer()

    #
    #
    #  Message dispatcher
    #
    #
    def on_message(self, message, transport):
        """
        received message from bus
        :param message: message object
        """
        assert type(message) is messaging.Message
        message_type = message.type

        if message_type == MessageType.CREATE_POINT:
            self.__on_message_create_point(message)

        elif message_type == MessageType.REMOVE_POINT:
            self.__on_message_remove_point(message)

        elif message_type == MessageType.JOIN_ROOM:
            self.__on_message_join(message)

        elif message_type == MessageType.UNJOIN_ROOM:
            self.__on_message_unjoin(message)

        elif message_type == MessageType.SDP_ANSWER:
            self.set_remote_sdp(message)

        elif message_type == MessageType.SEND_DTMF:
            self.__send_dtmf(message)

        else:
            LOG.warning("Unknown message type: %s", repr(message_type))

    def __on_message_create_point(self, message):
        try:
            point = self.__manager.create_point(point_id=str(message.point_id),
                                                initiator_message=message,
                                                config=self.__config,
                                                balancer=self.__balancer,
                                                transcoding_factory=self.__transcoding_factory)

            if message.has("cc") and message.has("vv"):
                profile_name = message.get("profile", "")
                profile = self.__config.profile(profile_name)
                assert profile is not None
                try:
                    point.event(PointEvent.CREATE_OFFER,
                                cc=message.get("cc"),
                                vv=message.get("vv"),
                                profile=profile)
                except PointControllerError:
                    self.__remove_point(point)
            else:
                LOG.warning("No cc or vv in initiator message")
                LOG.warning("Answer model not implemented")
        except ManagerError as e:
            LOG.warning(str(e))

    def __remove_point(self, point):
        assert type(point) is PointController
        LOG.debug("MC: removing point [%s]", point.point_id)
        try:
            self.__manager.remove_point(point.point_id)
        except ManagerError as e:
            LOG.warning(str(e))

    def __on_message_remove_point(self, message):
        try:
            self.__manager.remove_point(str(message.point_id))
        except ManagerError as e:
            LOG.warning(str(e))

    def remove_room(self, room):
        self.__manager.remove_room(room.room_id)

    def set_remote_sdp(self, message):
        point_id = str(message.point_id)
        point = self.__get_point_by_id(point_id)

        if point is not None:
            point.event(PointEvent.SDP_ANSWER, sdp=str(message.get("sdp", "")))
        else:
            LOG.warning("Unknown point " + str(point_id))

    def __on_message_join(self, message):
        try:
            point_id = str(message.point_id)
            room_id = str(message.room_id)
            self.__manager.join_room(point_id, room_id)
        except ManagerError as e:
            LOG.warning(str(e))

    def __on_message_unjoin(self, message):
        try:
            point_id = str(message.point_id)
            self.__manager.unjoin(point_id)
        except ManagerError as e:
            LOG.warning(str(e))

    def __send_dtmf(self, message):
        point_id = str(message.point_id)
        point = self.__get_point_by_id(point_id)
        if point is None:
            LOG.warning("Attempt to unjoin with unexisting point")
            return
        point.event("SEND_DTMF", dtmf=str(message.get("dtmf", "")))

if __name__ == "__main__":
    from a3.config import CommandLineConfig, IniConfig, DefaultConfig
    from a3.transcoding.gst1.factory import Gst1TranscodingFactory

    config = CommandLineConfig(IniConfig(DefaultConfig()))
    LOG.info("Config:\n%s", config)

    # TODO: implement configuration-based tanscoding
    transcoding_factory = Gst1TranscodingFactory()

    media_controller = MediaController(config, transcoding_factory)

    messaging.create(config.mq, media_controller).listen()

    while True:
        time.sleep(1)
        media_controller.on_timer()
