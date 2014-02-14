#!/usr/bin/env python
"""
Message class


"""


from serdes import IMessage, ISerDes
from transport import MessagingTransport


class Message(IMessage):
    """
    Message implementation
    """
    def __init__(self, type_, data=None):
        assert type(type_) is str
        self.__type = type_
        self.__data = data if data is not None else {}

        self.__channel = None
        self.__serdes = None
        self.__transport = None

    @property
    def channel(self):
        return self.__channel

    @channel.setter
    def channel(self, val):
        assert val is None or type(val) is str
        self.__channel = val

    @property
    def serdes(self):
        return self.__serdes

    @serdes.setter
    def serdes(self, value):
        assert value is None or isinstance(value, ISerDes)
        self.__serdes = value

    @property
    def transport(self):
        return self.__transport

    @transport.setter
    def transport(self, value):
        assert value is None or isinstance(value, MessagingTransport)
        self.__transport = value

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, val):
        assert not "MESSAGE TYPE SETTER DEPRECATED"
        #self.__type = val

    @property
    def sender(self):
        return str(self.get("sender"))

    @sender.setter
    def sender(self, value):
        assert type(value) is str
        self.set("sender", value)

    @property
    def point_id(self):
        return str(self.get("pointId"))

    @property
    def room_id(self):
        return str(self.get("roomId"))

    def set(self, key, value):
        self.__data[key] = value

    def get(self, key, default_value=None):
        return self.__data[key] if key in self.__data else default_value

    def has(self, key):
        return key in self.__data

    def all(self):
        return self.__data.iteritems()

    def delete(self, name):
        if name in self.__data:
            del self.__data[name]

    def extend(self, data=None):
        if data is not None:
            for name, value in data.iteritems():
                self.set(name, value)

    def forward(self, channel, message_type, data=None):
        assert type(channel) is str
        assert type(message_type) is str

        m = Message(message_type)
        m.extend(self.__data)
        m.extend(data)

        m.transport = self.transport
        m.serdes = self.serdes
        m.channel = channel

        self.transport.send_message(m)

    def reply(self, message_type, data=None):
        """
        reply: forward the message to its sender and override type and data if necassary
        """
        self.forward(self.sender, message_type, data)

    def to_str(self, spaces):
        s = " " * spaces
        result = s + "type=" + repr(self.type) + "\n"
        for n, v in self.__data.iteritems():
            vv = str(v).replace("\n", "\\n").replace("\r", "")
            if len(vv) > 60:
                vv = vv[:60] + "..."
            result += s + str(n) + "=" + vv + "\n"
        return result


class Factory(object):
    def create_message(self, message_type):
        assert type(message_type) is str
        m = Message(message_type)
        return m

