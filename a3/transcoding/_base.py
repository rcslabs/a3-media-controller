#!/usr/bin/env python
"""
Base transcoding objects
"""


__author__ = 'RCSLabs'


from abc import ABCMeta, abstractmethod


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


class IRtpFrontend(object):
    __metaclass__ = ABCMeta


class IDtmfSender(IMediaDestinationProvider, IMediaSourceProvider):
    __metaclass__ = ABCMeta

    @abstractmethod
    def send_dtmf(self, dtmf):
        """
        send dtmf
        """

    @abstractmethod
    def add_to_pipeline(self, pipeline):
        """
        add to pipeline
        """

    @abstractmethod
    def remove_from_pipeline(self, pipeline):
        """
        add to pipeline
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
        """

    @abstractmethod
    def create_transcoding_context(self):
        """
        :return: Object on which transcoding works
        :rtype : ``ITranscodingContext``
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

