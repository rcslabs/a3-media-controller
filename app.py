#!/usr/bin/env python

#
# should be moved to app module
#

import logging
import random

import messaging


class AppService(object):
    SERVER = "192.168.1.38"
    PORT = None
    SERVICE = "ekassir"
    #MEDIA_CONTROLLER = "media-controller"
    MEDIA_CONTROLLER = "mc:anton"


class MESSAGE_TYPE:
    START_SESSION = "START_SESSION"
    SESSION_STARTING = "SESSION_STARTING"
    SESSION_STARTED = "SESSION_STARTED"
    SESSION_FAILED = "SESSION_FAILED"

    START_CALL = "START_CALL"

    CALL_STARTING = "CALL_STARTING"
    CALL_STARTED = "CALL_STARTED"
    CALL_FINISHED = "CALL_FINISHED"
    CALL_FAILED = "CALL_FAILED"

    SDP_OFFER = "SDP_OFFER"
    SDP_ANSWER = "SDP_ANSWER"


class Session(object):
    def __init__(self, user):
        assert type(user) is User
        self.__session_id = str(random.getrandbits(32))
        self.__user = user
        self.__call = None

    @property
    def session_id(self):
        return self.__session_id

    @property
    def user(self):
        return self.__user

    @property
    def call(self):
        return self.__call

    @call.setter
    def call(self, call):
        self.__call = call


class SessionManager(object):
    def __init__(self):
        self.__sessions = dict()

    def has_session(self, session_id):
        assert type(session_id) is str
        return session_id in self.__sessions

    def get_session(self, session_id):
        assert type(session_id) is str
        return self.__sessions[session_id] if session_id in self.__sessions else None

    def add_user(self, user):
        assert type(user) is User
        session = Session(user)
        self.__sessions[session.session_id] = session
        return session

    def get_session_for_user(self, username):
        assert type(username) is str
        for session in self.__sessions.values():
            if session.user.name == username:
                return session
        return None


class User(object):
    def __init__(self, name, password=None):
        assert type(name) is str
        assert password is None or type(password) is str
        self.__name = name
        self.__password = password

    @property
    def name(self):
        return self.__name

    def accept(self, name, password=None):
        """
        Return bool
        """
        assert type(name) is str
        assert password is None or type(password) is str
        return name == self.__name and (self.__password is None or self.__password == password)


class UserManager(object):
    def __init__(self, message_dispatcher, session_manager):
        self.__users = []
        self.__session_manager = session_manager
        message_dispatcher.subscribe([MESSAGE_TYPE.START_SESSION], self)
        # DEBUG
        self.__users.append(User("terminal"))
        self.__users.append(User("operator", "1234"))

    def accept(self, username, password=None):
        """
        Return user if found or None
        """
        for user in self.__users:
            if user.accept(username, password):
                return user
        return None

    def on_message(self, message):
        if message.type == MESSAGE_TYPE.START_SESSION:
            if message.has("sessionId"):
                if self.__session_manager.has_session(message.get("sessionId")):
                    message.reply(MESSAGE_TYPE.SESSION_STARTED)
                else:
                    message.reply(MESSAGE_TYPE.SESSION_FAILED)
            elif message.has("username"):
                user = self.accept(str(message.get("username")), str(message.get("password")))
                if user is not None:
                    session = self.__session_manager.add_user(user)
                    message.reply(MESSAGE_TYPE.SESSION_STARTED, {"sessionId": session.session_id})
                else:
                    message.reply(MESSAGE_TYPE.SESSION_FAILED)
            else:
                message.reply(MESSAGE_TYPE.SESSION_FAILED)


class Call(object):
    def __init__(self, a_session, b_session):
        self.__id = "call-" + str(random.getrandbits(32))
        self.__a_session = a_session
        self.__b_session = b_session

        self.__a_message = None
        self.__b_message = None

    @property
    def call_id(self):
        return self.__id

    def __call_failed(self, reason):
        if self.__a_message is not None:
            self.__a_message.forward("sid:" + self.__a_session.session_id,
                                     MESSAGE_TYPE.CALL_FAILED,
                                     {"reason": reason, "callId": self.__id})

    def on_message(self, message):
        if message.type == MESSAGE_TYPE.START_CALL:
            self.__a_message = message
            if self.__a_session.call is not None:
                self.__call_failed("MULTIPLE CALLS NOT IMPLEMENTED")
            elif self.__b_session is None:
                self.__call_failed("UNAVAILABLE")
            elif self.__b_session.user.name == self.__a_session.user.name:
                self.__call_failed("SELF_CALL")
            elif self.__b_session.call is not None:
                self.__call_failed("BUSY")
            else:
                self.__a_session.call = self
                self.__b_session.call = self
                message.forward(AppService.MEDIA_CONTROLLER, "CREATE_MEDIA_POINT")
                message.forward("sid:" + self.__b_session.session_id, "INCOMING_CALL")


class CallManager(object):
    def __init__(self, message_dispatcher, session_manager):
        assert type(session_manager) is SessionManager
        self.__session_manager = session_manager
        message_dispatcher.subscribe([MESSAGE_TYPE.START_CALL], self)

    def on_message(self, message):
        session_id = str(message.get("sessionId"))
        if session_id is None:
            message.reply(MESSAGE_TYPE.SESSION_FAILED)
            return

        session = self.__session_manager.get_session(session_id)

        if message.type == MESSAGE_TYPE.START_CALL:
            b_session = self.__session_manager.get_session_for_user(str(message.get("bUri")))
            call = Call(session, b_session)
            call.on_message(message)


class MessageDispatcher(messaging.IMessageListener):
    def __init__(self):
        self.__listeners = {}

    def subscribe(self, message_types, listener):
        for message_type in message_types:
            if message_type not in self.__listeners:
                self.__listeners[message_type] = []
            self.__listeners[message_type].append(listener)

    def on_message(self, message, transport):
        print "Received: ", message.to_str(20)
        if message.type in self.__listeners:
            for listener in self.__listeners[message.type]:
                listener.on_message(message)


class App(object):
    
    def __init__(self):
        self.__message_dispatcher = MessageDispatcher()

        fmt = a3.messaging.serdes.JsonSerDes(a3.messaging.message.Factory())
        self.__messaging_transport = a3.messaging.serdes_transport.SerDesTransport(
            a3.messaging.transport.RedisTransport(AppService.SERVER, AppService.PORT, AppService.SERVICE),
            fmt)
        self.__messaging_transport.listener = self.__message_dispatcher

        self.__session_manager = SessionManager()
        self.__user_manager = UserManager(self.__message_dispatcher, self.__session_manager)
        self.__call_manager = CallManager(self.__message_dispatcher, self.__session_manager)

    def start(self):
        print "Starting app..."
        self.__messaging_transport.listen()


if __name__ == "__main__":
    FORMAT = '%(asctime)-15s %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.DEBUG)

    from config import Config
    config = Config()

    app = App()
    app.start()
