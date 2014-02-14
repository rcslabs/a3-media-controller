#!/usr/bin/env python


from transport import MessagingTransport, IMessageListener
from serdes import ISerDes, ParseException
from message import Message


import logging


LOGGER = logging.getLogger("MC")


class SerDesTransport(MessagingTransport, IMessageListener):
    """
    Decorates transport with serializer/deserializer
    """
    def __init__(self, transport, serdes):
        assert isinstance(transport, MessagingTransport)
        assert isinstance(serdes, ISerDes)
        MessagingTransport.__init__(self)
        self.__transport = transport
        self.__serdes = serdes
        transport.listener = self

    def send_message(self, message, channel=None):
        assert type(message) is Message
        if channel is None:
            channel = message.channel
        assert type(channel) is str

        LOGGER.info("<- sending <" + repr(channel) + ">:\n" + message.to_str(20))
        message.set("sender", self.__transport.channel_name)
        str_message = self.__serdes.serialize(message)
        self.__transport.send_message(str_message, channel)

    def listen(self):
        self.__transport.listen()

    def on_message(self, str_message, transport):
        assert type(str_message) is str
        try:
            message = self.__serdes.deserialize(str_message)
            message.transport = self
            LOGGER.info("-> received :\n" + message.to_str(20))
            self.message_received(message)
        except ParseException:
            LOGGER.exception("Corrupted message %s", str_message)

    @property
    def channel_name(self):
        return self.__transport.channel_name
