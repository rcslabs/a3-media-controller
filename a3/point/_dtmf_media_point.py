#!/usr/bin/env python
"""
    DtmfMediaPoint

    TODO: implement IDtmfSender with one method send_dtmf
    rename current IDtmfSender



                +----------------------- DtmfMediaPoint ------------------------+
                !                                                               !
                !                    IDtmfSender                                !
                !                   +----------+                                !
    RAW ------->!------------------>!  input   !        +-------+               !
                !                   !          !  link  ! media !               !
                !     +---------+   ! selector !------->! point !               !
                !     ! dtmfsrc !-->!          !        !       !--> udp        !
                !     +---------+   !          !        !       !<-- udp        !
                !                   +----------+        !       !--> udp        !
                !                                       !       !<-- udp        !
   Codec <------!<--------------------------------------!       !               !
                !                                       !       !               !
                !                                       +-------+               !
                !                                                               !
                +---------------------------------------------------------------+

"""

__author__ = 'RCSLabs'


from a3.transcoding import ITranscodingFactory, IDtmfSender, ITranscodingContext
from ._media_point_decorator import MediaPointDecorator


class DtmfMediaPoint(MediaPointDecorator):
    def __init__(self, media_point, transcoding_factory):
        assert isinstance(transcoding_factory, ITranscodingFactory)
        super(DtmfMediaPoint, self).__init__(media_point)

        self.__transcoding_factory = transcoding_factory
        self.__dtmf_sender = self.__transcoding_factory.create_inband_dtmf_sender()
        assert isinstance(self.__dtmf_sender, IDtmfSender)

        self.__inner_link = None
        self.__context = None

    def get_media_destination(self):
        """
                                     +---- DtmfSender -----+                        +-- media_point ---
                                     !                     !                        !
                 ... ----> dtmf_media_destination    dtmf_media_source ----> inner_media_destination
                                     !                     !                        !
                                     +---------------------+                        +------------------
        """
        assert self.__context is not None
        inner_media_destination = self._media_point.get_media_destination()
        dtmf_media_destination = self.__dtmf_sender.get_media_destination()
        dtmf_media_source = self.__dtmf_sender.get_media_source()
        self.__inner_link = self.__transcoding_factory.create_link(self.__context, dtmf_media_source, inner_media_destination)
        return dtmf_media_destination

    def set_context(self, context):
        assert context is None or isinstance(context, ITranscodingContext)
        self.__context = context
        super(DtmfMediaPoint, self).set_context(context)
        self.__dtmf_sender.set_context(context)

    def send_dtmf(self, dtmf):
        self.__dtmf_sender.send_dtmf(dtmf)

    def start(self):
        self.__dtmf_sender.start()
        super(DtmfMediaPoint, self).start()

    def stop(self):
        self.__dtmf_sender.stop()
        super(DtmfMediaPoint, self).stop()

    def dispose(self):
        self.__dtmf_sender.stop()
        super(DtmfMediaPoint, self).dispose()
