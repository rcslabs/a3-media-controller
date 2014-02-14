#!/usr/bin/env python
"""


Examples:
    m = messaging.create("redis://127.0.0.1/channel", listener)
    m.listen()
"""

import transport
import serdes
import message
import serdes_transport
from .transport import IMessageListener
from .message import Message

from ..config import MessageQueueUrl


def _create_transport(url):
    assert type(url) is MessageQueueUrl

    if url.protocol == "amqp":
        return transport.RabbitmqTransport(url.server, url.port, url.channel)
    elif url.protocol == "redis":
        return transport.RedisTransport(url.server, url.port, url.channel)
    else:
        raise Exception("Unknown protocol for MQ: ")


def create(url, listener=None):
    """
    Parse url and create message queue object
    """
    assert type(url) is MessageQueueUrl
    assert listener is None or isinstance(listener, IMessageListener)

    fmt = serdes.JsonSerDes(message.Factory())
    t = serdes_transport.SerDesTransport(
        transport.ThreadedMessagingTransport(_create_transport(url)),
        fmt)
    t.listener = listener
    return t

