#!/usr/bin/env python
"""

"""


from base import ISerDes, ParseException, IMessage
import json
import logging


LOGGER = logging.getLogger("MC")


class JsonSerDes(ISerDes):
    """
    Accepts messages in JSON format
    """
    def __init__(self, message_factory):
        self.__message_factory = message_factory

    def serialize(self, message):
        assert isinstance(message, IMessage)
        o = {"type": message.type}
        for (name, value) in message.all():
            o[name] = value
        return json.dumps(o)

    def deserialize(self, string):
        assert type(string) is str
        try:
            json_message = json.loads(string)
        except ValueError:
            LOGGER.error("Failed to parse JSON %s", string)
            raise ParseException("Error parsing message")

        if "type" not in json_message:
            raise ParseException("No message type")

        message = self.__message_factory.create_message(str(json_message["type"]))

        for key in json_message:
            if key != "type":
                message.set(key, json_message[key])

        message.serdes = self

        return message
