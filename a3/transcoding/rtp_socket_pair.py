#!/usr/bin/env python
"""
Open two ports from profile
"""


from ..logging import LOG
from ..config.profile import Profile
from ._base import ITranscodingFactory
from ._socket import ISocket, SocketError


class RtpSocketPair(object):
    def __init__(self, profile, transcoding_factory):
        assert type(profile) is Profile
        assert isinstance(transcoding_factory, ITranscodingFactory)
        self.__transcoding_factory = transcoding_factory
        self._rtp_socket = None
        self._rtcp_socket = None

        for (rtp_port, rtcp_port) in profile.ports_range:
            if self._try_open(rtp_port, rtcp_port, profile.interface):
                return

        # TODO: raise PortNotFound

    def _try_open(self, rtp_port, rtcp_port, interface="0.0.0.0"):
        try:
            self._rtp_socket = self.__transcoding_factory.create_socket(rtp_port, interface)
            self._rtcp_socket = self.__transcoding_factory.create_socket(rtcp_port, interface)
            assert isinstance(self._rtp_socket, ISocket)
            assert isinstance(self._rtcp_socket, ISocket)
            LOG.debug("RtpSocketPair.Succeeded %d, %d", rtp_port, rtcp_port)
            return True

        except SocketError:
            self.close()
            return False

    @property
    def rtp_socket(self):
        return self._rtp_socket

    @property
    def rtcp_socket(self):
        return self._rtcp_socket

    @property
    def rtp_port(self):
        return self._rtp_socket.port

    @property
    def rtcp_port(self):
        return self._rtcp_socket.port

    def close(self):
        if self._rtp_socket:
            self._rtp_socket.close()
            self._rtp_socket = None
        if self._rtcp_socket:
            self._rtcp_socket.close()
            self._rtcp_socket = None

    def __nonzero__(self):
        return bool(self._rtp_socket and self._rtcp_socket)


if __name__ == "__main__":
    pass
