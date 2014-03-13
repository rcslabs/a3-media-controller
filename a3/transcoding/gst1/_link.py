#! /usr/bin/env python
"""
Link

creates transcoding between MediaSource and MediaDestination


Curently accepts only Codec (NO RTP CODEC of FLVMUXED)

There is a problem in gstreamer:

         +- rtpbin -+         +- rtpbin -+
         !          !         !          !
  udp -->!          +-------->+          !<-- udp
  udp <--!          !         !          !--> udp
  udp -->!          !         !          !<-- udp
  udp <--!          +<--------+          !--> udp
         !          !         !          !
         +----------+         +----------+

In such configuration rtpbin DOES NOT change ssrc to its internal

So in current implementation MediaPoint takes care of depay (pay) and provides (accepts) base Codec

"""


__author__ = 'RCSLabs'


from ...logging import LOG
from ...media import MediaType, Codec, RtpCodec
from ._pads import MediaSource, MediaDestination, VirtualMediaSource, VirtualMediaDestination
from ._elements import GstPipeline
from ._endec import create_decoder, create_encoder


class Link(object):
    """
    :type Link.__media_source: MediaSource
    """
    def __init__(self, context, media_source, media_destination):
        """
        :type context: GstPipeline
        :type media_source: VirtualMediaSource
        :type media_destination: VirtualMediaSource
        """
        assert type(context) is GstPipeline
        assert isinstance(media_source, VirtualMediaSource)
        assert isinstance(media_destination, VirtualMediaDestination)

        self.__context = context

        self.__media_source = None
        self.__media_destination = None

        self.__decoder = None
        self.__encoder = None

        media_source.subscribe(self.__media_source_resolved)
        media_destination.subscribe(self.__media_destination_resolved)

    def set_context(self, context):
        LOG.debug("Link.set_context %s", str(context))
        if self.__context is context:
            return

        if self.__context:
            if self.__decoder:
                self.__context.remove(self.__decoder)
            if self.__encoder:
                self.__context.remove(self.__encoder)
            self.__context = None

        # TODO:
        # self.__context = context
        # if self.__context:
        #   add and create links

    def __media_source_resolved(self, media_source):
        """
        :type media_source: MediaSource
        """
        assert type(media_source) is MediaSource
        assert self.__media_source is None
        LOG.debug("transcoding.Link: resolved %s", str(media_source))
        self.__media_source = media_source
        if self.__media_source and self.__media_destination:
            self.__perform_link(self.__media_source, self.__media_destination)

    def __media_destination_resolved(self, media_destination):
        assert type(media_destination) is MediaDestination
        assert self.__media_destination is None
        LOG.debug("transcoding.Link: resolved %s", str(media_destination))
        self.__media_destination = media_destination

        if self.__media_source and self.__media_destination:
            self.__perform_link(self.__media_source, self.__media_destination)

    def __perform_link(self, media_source, media_destination):
        assert type(media_source) is MediaSource
        assert type(media_destination) is MediaDestination
        assert len(media_destination.acceptable_codecs) > 0
        LOG.debug("transcoding.Link: Perform link %s -> %s", media_source, media_destination)

        source_pad = media_source.gst_pad
        source_codec = media_source.codec
        destination_pad = media_destination.gst_pad
        destination_codecs = media_destination.acceptable_codecs

        if media_source.is_raw() and media_destination.accepts_raw():
            LOG.debug("transcoding.Link: Selected RAW")
            source_pad.link(destination_pad)

        elif media_destination.accepts(source_codec):
            LOG.debug("transcoding.Link: Selected DIRECT %s", source_codec)
            source_pad.link(destination_pad)

        elif media_destination.accepts_raw():
            LOG.debug("transcoding.Link: Decode %s -> RAW", source_codec)

            # decoder (-> encoder)
            self.__decoder = create_decoder(source_codec)
            self.__context.add(self.__decoder)
            self.__decoder.src_pad.link(self.__media_destination.gst_pad)

            # source (-> decoder)
            self.__media_source.gst_pad.link(self.__decoder.sink_pad)

        elif self.__media_source.is_raw():
            destination_codec = destination_codecs[0]
            LOG.debug("transcoding.Link: Encode RAW -> %s", destination_codec)

            # encoder (-> Destination)
            self.__encoder = create_encoder(destination_codec)
            self.__context.add(self.__encoder)
            self.__encoder.element.sync_state_with_parent()
            self.__encoder.src_pad.link(self.__media_destination.gst_pad)

            # source (-> encoder)
            self.__media_source.gst_pad.link(self.__encoder.sink_pad)

        else:
            destination_codec = destination_codecs[0]
            assert type(source_codec) is Codec
            assert type(destination_codec) is Codec
            LOG.debug("transcoding.Link: Transcode %s -> %s", source_codec, destination_codec)

            # encoder (-> Destination)
            self.__encoder = create_encoder(destination_codec)
            self.__context.add(self.__encoder)
            self.__encoder.src_pad.link(self.__media_destination.gst_pad)

            # decoder (-> encoder)
            self.__decoder = create_decoder(source_codec)
            self.__context.add(self.__decoder)
            self.__decoder.src_pad.link(self.__encoder.sink_pad)

            # source (-> decoder)
            self.__media_source.gst_pad.link(self.__decoder.sink_pad)

    def dispose(self):
        assert self.__context is None
        LOG.debug("Link.dispose")
        if self.__decoder:
            self.__decoder.dispose()
            del self.__decoder

        if self.__encoder:
            self.__encoder.dispose()
            del self.__encoder

