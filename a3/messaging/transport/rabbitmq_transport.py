#!/usr/bin/env python
"""
RabbitMQ message transport
"""


from _base import MessagingTransport


class RabbitmqTransport(MessagingTransport):
    def __init__(self, server, port, channel_name):
        MessagingTransport.__init__(self)
        self.__channel_name = channel_name

        import pika
        self.__connection = pika.BlockingConnection(pika.ConnectionParameters(server, port))
        self.__channel = self.__connection.channel()
        self.__channel.queue_declare(queue=channel_name)

    def send_message(self, message, channel=None):
        assert type(channel) is str
        self.__channel.basic_publish(exchange='',
                                     routing_key=channel,
                                     body=str(message))

    def listen(self):
        self.__channel.basic_consume(lambda ch, method, properties, body: self.message_received(body),
                                     queue=self.__channel_name,
                                     no_ack=True)
        self.__channel.start_consuming()

    @property
    def channel_name(self):
        return self.__channel_name
