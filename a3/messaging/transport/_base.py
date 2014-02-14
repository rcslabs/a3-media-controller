#!/usr/bin/env python
"""

"""

from abc import ABCMeta, abstractmethod, abstractproperty
import threading


class IMessageListener(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def on_message(self, message, transport):
        """
        Callback on each received message
        :param message: string message received
        :param transport: message queue
        """


class MessagingTransport(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.__listener = None

    @property
    def listener(self):
        return self.__listener

    @listener.setter
    def listener(self, val):
        assert val is None or isinstance(val, IMessageListener)
        self.__listener = val

    def message_received(self, str_message):
        if self.__listener is not None:
            self.__listener.on_message(str_message, self)

    @abstractmethod
    def send_message(self, message, channel=None):
        """
        Send message to channel
        :param message: message to send
        :param channel: str channel name
        """

    @abstractmethod
    def listen(self):
        """
        start listening queue
        """

    @abstractproperty
    def channel_name(self):
        """
        return message queue channel name
        """


class ThreadedMessagingTransport(MessagingTransport, threading.Thread, IMessageListener):
    """
    Decorates transport to run in thread
    """
    def __init__(self, transport):
        assert isinstance(transport, MessagingTransport)
        MessagingTransport.__init__(self)
        threading.Thread.__init__(self)
        self.__transport = transport
        transport.listener = self

    def run(self):
        """
        thread function
        """
        self.__transport.listen()

    def send_message(self, message, channel=None):
        self.__transport.send_message(message, channel)

    def listen(self):
        self.daemon = True
        self.start()

    def on_message(self, message, transport):
        self.message_received(message)

    @property
    def channel_name(self):
        return self.__transport.channel_name
