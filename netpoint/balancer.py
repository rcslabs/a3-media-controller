#!/usr/bin/env python

"""Balancer


"""

from netpoint.rtp_point_agent import RtpPointAgent

import logging
LOGGER = logging.getLogger("MC")


class SingletonMeta(type):
    def __init__(cls, *args, **kw):
        cls.instance = None

    def __call__(cls, *args, **kw):
        if cls.instance is None:
            cls.instance = super(SingletonMeta, cls).__call__(*args, **kw)
        return cls.instance


class Balancer(object):
    __metaclass__ = SingletonMeta

    def __init__(self):
        self.rtp_agents = []

    def get_rtp_agent(self):
        """ returns stun agent"""
        for agent in self.rtp_agents:
            if agent.count < 10:                         # no more then 10 connections per agent
                return agent

        agent = RtpPointAgent("127.0.0.1")
        agent.start()
        self.rtp_agents.append(agent)
        return agent
