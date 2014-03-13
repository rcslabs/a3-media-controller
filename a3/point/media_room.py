#!/usr/bin/env python
"""

"""

from a3.logging import LOG
from a3.media import MediaType
from _base import IMediaPoint
from a3.transcoding._base import ITranscodingFactory, IMediaDestination, IMediaSource


class MediaRoom(object):
    def __init__(self, media_type, transcoding_factory):
        assert type(media_type) is MediaType
        assert isinstance(transcoding_factory, ITranscodingFactory)
        self.__media_type = media_type
        self.__transcoding_factory = transcoding_factory

        self.__points = []
        self.__context = self.__transcoding_factory.create_transcoding_context()

    def join(self, media_point):
        assert isinstance(media_point, IMediaPoint)
        if media_point in self.__points:
            return
        assert len(self.__points) <= 1            # currently no more than 2 points in room
        self.__points.append(media_point)
        self.__add_point_to_pipeline(media_point)
        if len(self.__points) == 2:
            self.__link_points(self.__points[0], self.__points[1])
            self.__link_points(self.__points[1], self.__points[0])
            LOG.debug("MediaRoom.starting pipeline")
            self.__context.play()
            for p in self.__points:
                p.force_key_unit()

    def unjoin(self, media_point):
        assert isinstance(media_point, IMediaPoint)
        if media_point in self.__points:
            if len(self.__points) == 2:
                LOG.debug("MediaRoom.stopping pipeline")
                self.__context.stop()
            self.__points.remove(media_point)
            self.__remove_point_from_pipeline(media_point)

    def __add_point_to_pipeline(self, media_point):
        LOG.debug("MediaRoom.add_point %s", media_point.point_id)
        assert isinstance(media_point, IMediaPoint)
        media_point.add_to_pipeline(self.__context)

    def __remove_point_from_pipeline(self, media_point):
        LOG.debug("MediaRoom.remove_point %s", media_point.point_id)
        assert isinstance(media_point, IMediaPoint)
        media_point.remove_from_pipeline(self.__context)

    def __link_points(self, a, b):
        assert isinstance(a, IMediaPoint)
        assert isinstance(b, IMediaPoint)

        media_source = a.get_media_source()
        media_destination = b.get_media_destination()
        assert isinstance(media_source, IMediaSource)
        assert isinstance(media_destination, IMediaDestination)

        transcoded_link = self.__transcoding_factory.create_link(self.__context, media_source, media_destination)
        #media_source.link(media_destination)
        a.force_key_unit()
