#!/usr/bin/env python
"""
RtpPointAgent
communicates with one running instance of stun-agent

"""


from agent import Agent
from a3.config.profile import Profile

import random
import logging


LOGGER = logging.getLogger("MP")


class Conn(object):
    def __init__(self, conn_id, host, port, agent):
        assert(type(conn_id) is str)
        assert(type(host) is str)
        assert(type(port) is int)
        self.__id = conn_id
        self.__host = host
        self.__port = port
        self.__agent = agent

    def send_message(self, message):
        message["connId"] = self.__id
        self.__agent.send_message(message)

    @property
    def id(self):
        return self.__id

    @property
    def host(self):
        return self.__host

    @property
    def port(self):
        return self.__port

    def __str__(self):
        return "Conn: %s:%s" % (self.__host, self.__port)


#REQUESTING_MARK = "requesting"


class RtpPointAgent(Agent):

    def __init__(self, host):
        self.__default_host = host
        self.__callbacks = {}
        self.__conns = []
        Agent.__init__(self, "stun-agent", "STUN")

    @property
    def count(self):
        return len(self.__conns)

    @property
    def host(self):
        return self.__default_host

    def request_conn(self, profile, callback):
        assert type(profile) is Profile
        LOGGER.info("RtpPointAgent::request_conn profile=%s", str(profile))
        request_id = str(random.getrandbits(32))
        self.__callbacks[request_id] = callback
        self.__conns.append(request_id)
        self.send_message({"type":      "OPEN_CONN",
                           "iface":     profile.interface,
                           "port":      "%d-%d" % (profile.ports_range.start, profile.ports_range.end),
                           "requestId": request_id})

    def close_conn(self, conn):
        if conn in self.__conns:
            self.__conns.remove(conn)
            self.send_message(dict(type="CLOSE_CONN", id=conn.id))

    def __on_conn_ok(self, msg):
        conn_port = int(msg["port"])
        conn_id = msg["id"]
        conn_host = msg["iface"] if msg["iface"] != "0.0.0.0" else self.__default_host
        request_id = msg["requestId"]

        self.__conns.remove(request_id)

        conn = Conn(conn_id, conn_host, conn_port, self)
        self.__conns.append(conn)

        if request_id not in self.__callbacks:
            LOGGER.warn("[WARNING] No callback ON NetPoint::OPEN_CONN_OK")
            self.close_conn(conn)
            return

        callback = self.__callbacks[request_id]
        del self.__callbacks[request_id]
        callback(conn)

    def __on_conn_failed(self, msg):
        request_id = msg["requestId"]

        self.__conns.remove(request_id)

        if request_id not in self.__callbacks:
            LOGGER.warn("No callback ON NetPoint::OPEN_PORT_FAILED")
            return

        callback = self.__callbacks[request_id]
        del self.__callbacks[request_id]
        callback(None)

    def on_message(self, msg, mq):
        msg_type = msg["type"]
        if msg_type == "OPEN_CONN_OK":
            self.__on_conn_ok(msg)
        elif msg_type == "OPEN_CONN_FAILED":
            self.__on_conn_failed(msg)
