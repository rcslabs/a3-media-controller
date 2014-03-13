#!/usr/bin/env python
"""
Base transcoding objects
"""


__author__ = 'RCSLabs'


from abc import ABCMeta, abstractmethod, abstractproperty


class IMediaSource(object):
    __metaclass__ = ABCMeta

    #@abstractmethod
    #def link(self, media_destination):
    #    """
    #    Link media to destination
    #    """


class IMediaDestination(object):
    pass


class ITranscodingContext(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def pause(self):
        pass

    @abstractmethod
    def play(self):
        pass

    @abstractmethod
    def dispose(self):
        pass


class IMediaSourceProvider(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_media_source(self):
        """
        will return media source
        """


class IMediaDestinationProvider(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_media_destination(self):
        """
        will return media destination
        """


class IRtpFrontend(IMediaSourceProvider, IMediaDestinationProvider):
    __metaclass__ = ABCMeta

    @abstractproperty
    def rtp_port(self):
        """
        :return: rtp port
        :rtype : int
        """

    @abstractproperty
    def rtcp_port(self):
        """
        :return: rtcp port
        :rtype : int
        """

    @abstractmethod
    def dispose(self):
        """
        destroy the object
        """


class IRtmpFrontend(IMediaSourceProvider, IMediaDestinationProvider):
    __metaclass__ = ABCMeta

    @abstractproperty
    def sub(self):
        """
        :return: subscribe rtmp url
        :rtype : str
        """

    @abstractproperty
    def pub(self):
        """
        :return: publish rtmp url
        :rtype : str
        """

    @abstractmethod
    def dispose(self):
        """
        destroy the object
        """


class IDtmfSender(IMediaDestinationProvider, IMediaSourceProvider):
    __metaclass__ = ABCMeta

    @abstractmethod
    def send_dtmf(self, dtmf):
        """
        send dtmf
        """

    @abstractmethod
    def set_context(self, context):
        """
        add/remove from transcoding context
        """

    @abstractmethod
    def dispose(self):
        """
        destroy element
        """


class ITranscodingFactory(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def create_socket(self, port, interface):
        """
        Method creates a new udp socket instance
        throws SocketError on network issues
        """

    @abstractmethod
    def create_rtp_frontend(self, media_type, profile):
        """
        create new rtp frontend
        :rtype : IRtpFrontend
        """

    @abstractmethod
    def create_rtmp_frontend(self, media_type, profile):
        """
        create new rtp frontend
        :rtype : IRtmpFrontend
        """

    @abstractmethod
    def create_transcoding_context(self):
        """
        :return: Object on which transcoding works
        :rtype : ITranscodingContext
        """

    @abstractmethod
    def create_inband_dtmf_sender(self):
        """
        return element of type IDtmfSender
        """

    @abstractmethod
    def create_link(self, context, media_source, media_destination):
        """
        link source to destination with transcoding
        """

    @abstractmethod
    def get_supported_codecs(self):
        """
        return list of supported codecs
        """
