#!/usr/bin/env python


from a3.logging import LOG
from a3.sdp.capabilities import Cc, Vv
from a3.sdp.factory import Factory as SdpFactory
from a3.sdp.error import SemanticError
from a3.sdp.raw.attributes.error import ParseError
from a3.transcoding._base import ITranscodingFactory
from .point import Point, IPointListener


class MessageType:
    CREATE_POINT = "CREATE_MEDIA_POINT"
    CREATE_POINT_OK = "CREATE_MEDIA_POINT_OK"
    CREATE_POINT_FAILED = "CREATE_MEDIA_POINT_FAILED"

    REMOVE_POINT = "REMOVE_MEDIA_POINT"
    REMOVE_POINT_OK = "REMOVE_MEDIA_POINT_OK"
    REMOVE_POINT_FAILED = "REMOVE_MEDIA_POINT_FAILED"

    JOIN_ROOM = "JOIN_ROOM"
    UNJOIN_ROOM = "UNJOIN_ROOM"
    SDP_OFFER = "SDP_OFFER"
    SDP_ANSWER = "SDP_ANSWER"

    CRITICAL_ERROR = "CRITICAL_ERROR"


class Event:
    CREATE_OFFER = "e:CREATE_OFFER"
    CREATE_ANSWER = "e:CREATE_ANSWER"
    SDP_ANSWER = "e:SDP_ANSWER"
    CONN_READY = "e:CONN_READY"
    REMOVE = "e:REMOVE"
    TIMER = "e:TIMER"


class State:
    START = "START"
    ERROR = "ERROR"
    CREATING_OFFER = "CREATING_OFFER"
    CREATING_ANSWER = "CREATING_ANSWER"
    WAITING_REMOTE_SDP = "WAITING_REMOTE_SDP"
    CONNECTED = "CONNECTED"
    CLOSED = "CLOSED"

#    WAIT_STREAMS = "WAIT_STREAMS"
#    WAIT_REMOTE_SDP = "WAIT_REMOTE_SDP"
#    RUNNING = "RUNNING"
#    CLOSED = "CLOSED"
#    ERROR = "ERROR"


class PointControllerError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class PointController(IPointListener):
    def __init__(self, point_id, initiator_message, config, balancer, transcoding_factory):
        assert isinstance(transcoding_factory, ITranscodingFactory)
        self.__point_id = point_id
        self.__initiator_message = initiator_message
        self.__config = config
        self.__balancer = balancer
        self.__transcoding_factory=transcoding_factory
        self.__state = State.START
        self.__room = None
        self.__point = None
        self.__room = None

    @property
    def point_id(self):
        return self.__point_id

    @property
    def point(self):
        return self.__point

    @property
    def room(self):
        return self.__room

    @room.setter
    def room(self, room):
        self.__room = room

    def reply(self, message_type, message_attributes=None):
        self.__initiator_message.reply(message_type, message_attributes)

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, new_state):
        LOG.debug("PointController[%s]: transition %s -> %s", self.__point_id, self.__state, new_state)
        self.__state = new_state

    def event(self, event_type, **kwargs):
        if event_type != Event.TIMER:
            LOG.debug("PointController[%s]: Got event %s in state %s",
                      self.__point_id, repr(event_type), repr(self.__state))

        if self.state == State.START:
            if event_type == Event.CREATE_OFFER:
                self.__create_offer(**kwargs)
            else:
                self.__unhandled_event(event_type)

        elif self.state == State.CREATING_OFFER:
            if event_type == Event.CONN_READY:
                LOG.debug("PointController.LOCAL-SDP=%s", self.__point.local_sdp)
                self.state = State.WAITING_REMOTE_SDP
                self.reply(MessageType.SDP_OFFER, {"sdp": str(self.__point.local_sdp)})
            elif event_type == Event.REMOVE:
                self.__remove()
                self.reply(MessageType.REMOVE_POINT_OK)
            elif event_type == Event.TIMER:
                pass
            else:
                self.__unhandled_event(event_type)

        elif self.state == State.WAITING_REMOTE_SDP:
            if event_type == Event.SDP_ANSWER:
                try:
                    self.state = State.CONNECTED
                    self.__on_remote_sdp(**kwargs)
                    self.reply(MessageType.CREATE_POINT_OK)
                except (ParseError, AssertionError) as err:
                    LOG.exception("Exception while parsing SDP-ANSWER: %s", str(err))
                    self.state = State.ERROR
                    self.reply(MessageType.CREATE_POINT_FAILED)

            elif event_type == Event.REMOVE:
                self.__remove()
                self.reply(MessageType.REMOVE_POINT_OK)
            elif event_type == Event.TIMER:
                pass
            else:
                self.__unhandled_event(event_type)

        elif self.state == State.CONNECTED:
            if event_type == Event.REMOVE:
                self.__remove()
                self.reply(MessageType.REMOVE_POINT_OK)
            elif event_type == Event.TIMER:
                self.__point.on_timer()
            elif event_type == "SEND_DTMF":
                self.__point.send_dtmf(kwargs["dtmf"])
            else:
                self.__unhandled_event(event_type)

        else:
            self.__unhandled_event(event_type)

    def __unhandled_event(self, event_type):
        LOG.warning("PointController: Unhandled event " + repr(event_type) + " in state " + repr(self.state))

    def __error(self, message):
        LOG.warning("PointController: Error: " + repr(message))
        self.state = State.ERROR
        raise PointControllerError(message)

    def __remove(self):
        if self.__point:
            self.__point.stop()
            self.__point.dispose()
            self.__point = None
        self.state = State.CLOSED

    def __create_offer(self, cc, vv, profile):
        assert self.__point is None

        # DEBUG!
        #if "H264/90000" in cc["video"]:
        #    cc["video"].remove("H264/90000")
        #    #cc["video"].insert(0, "H263-1998/90000")
        #    cc["video"].insert(0, "VP8/90000")

        try:
            sdp = SdpFactory.create_offer(Cc(cc), Vv(vv), self.__transcoding_factory.get_supported_codecs())
            self.state = State.CREATING_OFFER
            self.__point = Point(self.__point_id,
                                 listener=self,
                                 local_sdp=sdp,
                                 balancer=self.__balancer,
                                 config=self.__config,
                                 transcoding_factory=self.__transcoding_factory,
                                 profile=profile)
            self.__point.start()
        except SemanticError:
            self.reply(MessageType.CREATE_POINT_FAILED)
            self.__error("Error in CC/VV")

    def __on_remote_sdp(self, sdp):
        assert type(sdp) is str
        LOG.debug("PointController: remote SDP: %s", sdp)
        self.__point.remote_sdp = SdpFactory.create_from_string(sdp)

    #
    # IPointListener
    #
    def point_conn_ready(self):
        LOG.debug("PointController.point_conn_ready")
        self.event(Event.CONN_READY)
