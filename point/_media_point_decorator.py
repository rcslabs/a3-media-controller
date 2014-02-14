#!/usr/bin/env python
"""
RTP MediaPoint
"""

__author__ = 'RCSLabs'


from ._base import IMediaPoint, IMediaPointListener


class MediaPointDecorator(IMediaPoint, IMediaPointListener):
    def __init__(self, media_point):
        assert isinstance(media_point, IMediaPoint)
        self._media_point = media_point
        self._media_point.set_listener(self)
        self._listener = None

    #
    # IMediaPoint
    #
    @property
    def point_id(self):
        return self._media_point.point_id

    def set_listener(self, listener):
        assert isinstance(listener, IMediaPointListener)
        self._listener = listener

    def set_profile(self, profile):
        self._media_point.set_profile(profile)

    def start(self):
        self._media_point.start()

    def stop(self):
        self._media_point.stop()

    def dispose(self):
        self._media_point.dispose()

    def on_timer(self):
        self._media_point.on_timer()

    def set_local_media_description(self, local_media_description):
        self._media_point.set_local_media_description(local_media_description)

    def set_remote_media_description(self, remote_media_description):
        self._media_point.set_remote_media_description(remote_media_description)

    def add_to_pipeline(self, pipeline):
        self._media_point.add_to_pipeline(pipeline)

    def remove_from_pipeline(self, pipeline):
        self._media_point.remove_from_pipeline(pipeline)

    #
    # IMediaSourceProvider
    #
    def get_media_source(self):
        return self._media_point.get_media_source()

    #
    # IMediaDestinationProvider
    #
    def get_media_destination(self):
        return self._media_point.get_media_destination()

    #
    # IMediaPointListener
    #
    def media_point_frontend_ready(self, media_point):
        if self._listener is not None:
            self._listener.media_point_frontend_ready(self)

    #TODO: ???
    def force_key_unit(self):
        self._media_point.force_key_unit()
