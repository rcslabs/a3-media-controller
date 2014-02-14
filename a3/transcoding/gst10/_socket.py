"""
Gstreamer 0.10 socket
"""


from .._base import Socket as BaseSocket, SocketException
import socket


class Socket(BaseSocket):
    def __init__(self, port, interface="0.0.0.0"):
        super(Socket, self).__init__(port, interface)
        assert type(port) is int
        assert type(interface) is str

        try:
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.__socket.bind((interface, port))
            self.__port = self.__socket.getsockname()[1]
        except socket.error:
            raise SocketException("Socket error")

    def close(self):
        self.__socket.close()
        self.__socket = None

    @property
    def port(self):
        if self.__socket is None:
            raise SocketException("Socket error")
        return self.__port

    @property
    def socket(self):
        return self.__socket

    @property
    def fileno(self):
        return self.__socket.fileno()


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
            self.failUnlessRaises(SocketException, Socket, INVALID_PORT)
            s = Socket(VALID_PORT)
            s.close()
            self.failUnlessRaises(SocketException, Socket, INVALID_PORT, "127.0.0.1")
            s = Socket(VALID_PORT, "127.0.0.1")
            s.close()

        def test_close(self):
            s = Socket(VALID_PORT)
            s.close()
            s = Socket(VALID_PORT)
            s.close()

        def test_multiply_open(self):
            s = Socket(VALID_PORT)
            self.failUnlessRaises(SocketException, Socket, VALID_PORT)
            s.close()

        def test_0_port(self):
            s = Socket(0)
            assert type(s.port) is int and s.port >= 1024
            s.close()

    unittest.main()
