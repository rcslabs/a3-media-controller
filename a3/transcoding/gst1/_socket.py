#!/usr/bin/env python
"""
To run tests write

# python -m point.transcoding.gst1_transcoding.socket


"""


from .._socket import ISocket, SocketError
from ._base import GObject, GLib, Gio


class Socket(ISocket):
    def __init__(self, port, interface="0.0.0.0"):
        super(Socket, self).__init__(port, interface)
        assert type(port) is int
        assert type(interface) is str

        try:
            inet_addr = Gio.InetAddress.new_from_string(interface)
            socket_addr = Gio.InetSocketAddress.new(inet_addr, port)
            self.__socket = Gio.Socket.new(Gio.SocketFamily.IPV4, Gio.SocketType.DATAGRAM, Gio.SocketProtocol.DEFAULT)
            self.__socket.bind(socket_addr, False)
            # get port
            local_address = self.__socket.get_property("local_address")
            assert local_address is not None
            self.__port = int(local_address.get_property("port"))

        except GLib.GError:
            raise SocketError("Socket error")

    def close(self):
        self.__socket.close()
        self.__socket = None

    @property
    def port(self):
        if self.__socket is None:
            raise SocketError("Socket error")
        return self.__port

    @property
    def socket(self):
        return self.__socket


if __name__ == "__main__":

    import unittest

    # random port that must be ready to open socket
    VALID_PORT = 32654

    # port that must be impossible to open socket
    INVALID_PORT = 80

    class TestSocket(unittest.TestCase):
        def test_syntax(self):
            self.failUnlessRaises(AssertionError, Socket, long(VALID_PORT))

        def test_open(self):
            self.failUnlessRaises(SocketError, Socket, INVALID_PORT)
            s = Socket(VALID_PORT)
            s.close()
            self.failUnlessRaises(SocketError, Socket, INVALID_PORT, "127.0.0.1")
            s = Socket(VALID_PORT, "127.0.0.1")
            s.close()

        def test_close(self):
            s = Socket(VALID_PORT)
            s.close()
            s = Socket(VALID_PORT)
            s.close()

        def test_multiply_open(self):
            s = Socket(VALID_PORT)
            self.failUnlessRaises(SocketError, Socket, VALID_PORT)
            s.close()

        def test_0_port(self):
            s = Socket(0)
            assert type(s.port) is int and s.port >= 1024
            s.close()

    unittest.main()
