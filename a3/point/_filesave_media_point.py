#!/usr/bin/env python
"""
    Filesave

    TODO: implement IDtmfSender with one method send_dtmf
    rename current IDtmfSender



                +--------------------- FilesaveMediaPoint ----------------------+
                !                                                               !
                !                                       +-------+               !
                !                                       ! media !               !
    RAW ------->!-------------------------------------->! point !               !
                !                                       !       !               !
                !                                       !       !               !
                !                       tee             !       !--> udp        !
                !                   +----------+        !       !<-- udp        !
   Codec <------!<------------------!          !        !       !--> udp        !
                !                   !          !        !       !<-- udp        !
                !         +------+  !          !<-------!       !               !
                !         !      !<-!          !        !       !               !
                !         +------+  !          !        +-------+               !
                !                   +----------+                                !
                +---------------------------------------------------------------+

"""

__author__ = 'RCSLabs'

from ..logging import LOG
from ..transcoding import ITranscodingFactory
from ..transcoding.gst1._base import Gst
from ..transcoding.gst1._pads import VirtualMediaSource, MediaSource
from ._media_point_decorator import MediaPointDecorator


class FilesaveMediaPoint(MediaPointDecorator):
    def __init__(self, media_point, transcoding_factory):
        assert isinstance(transcoding_factory, ITranscodingFactory)
        super(FilesaveMediaPoint, self).__init__(media_point)
        self.__transcoding_factory = transcoding_factory
        self.__context = None
        self.__media_source = VirtualMediaSource()
        self.__tee = None
        self.__fakesink = None

    def get_media_source(self):
        """
                                     +---------------------+                            +-- media_point ---
                                     !                     !                            !
                 ... <--------- __media_source       fs_media_destination <----- inner_media_source
                                     !                     !                            !
                                     +---------------------+                            +------------------
        """
        LOG.debug("FilesaveMediaPoint: get_media_source")
        assert self.__context is not None
        inner_media_source = self._media_point.get_media_source()
        inner_media_source.subscribe(self.__inner_media_source_resolved)
        return self.__media_source

    def __inner_media_source_resolved(self, inner_media_source):
        LOG.debug("FilesaveMediaPoint: __inner_media_source_resolved")

        tee = Gst.ElementFactory.make("tee", None)
        capsfilter1 = Gst.ElementFactory.make("capsfilter", None)
        capsfilter1.set_property("caps", Gst.caps_from_string("audio/x-alaw,channels=(int)1,rate=(int)8000"))
        capsfilter2 = Gst.ElementFactory.make("capsfilter", None)
        capsfilter2.set_property("caps", Gst.caps_from_string("audio/x-alaw,channels=(int)1,rate=(int)8000"))
        alawdec = Gst.ElementFactory.make("alawdec", None)
        waveenc = Gst.ElementFactory.make("wavenc", None)
        filesink = Gst.ElementFactory.make("filesink", None)
        filesink.set_property("location", "/tmp/" + self._media_point.point_id + ".wav")

        self.__context._element.add(filesink)
        filesink.sync_state_with_parent()

        self.__context._element.add(waveenc)
        waveenc.sync_state_with_parent()

        self.__context._element.add(alawdec)
        alawdec.sync_state_with_parent()

        self.__context._element.add(capsfilter1)
        capsfilter1.sync_state_with_parent()

        self.__context._element.add(capsfilter2)
        capsfilter2.sync_state_with_parent()

        self.__context._element.add(tee)
        tee.sync_state_with_parent()

        tee_sink, tee_src_1, tee_src_2 = tee.get_static_pad("sink"), tee.get_request_pad("src_%u"), tee.get_request_pad("src_%u"),
        assert tee_sink and tee_src_1 and tee_src_2

        capsfilter1_src, capsfilter1_sink = capsfilter1.get_static_pad("src"), capsfilter1.get_static_pad("sink")
        assert capsfilter1_src and capsfilter1_sink

        capsfilter2_src, capsfilter2_sink = capsfilter2.get_static_pad("src"), capsfilter2.get_static_pad("sink")
        assert capsfilter2_src and capsfilter2_sink

        filesink_sink = filesink.get_static_pad("sink")
        assert filesink_sink

        waveenc_src, waveenc_sink = waveenc.get_static_pad("src"), waveenc.get_static_pad("sink")
        assert waveenc_src and waveenc_sink

        alawdec_src, alawdec_sink = alawdec.get_static_pad("src"), alawdec.get_static_pad("sink")
        assert alawdec_src and alawdec_sink

        inner_media_source.gst_pad.link(tee_sink)
        tee_src_1.link(capsfilter1_sink)
        tee_src_2.link(capsfilter2_sink)

        capsfilter2_src.link(alawdec_sink)
        alawdec_src.link(waveenc_sink)
        waveenc_src.link(filesink_sink)

        self.__media_source.resolve(MediaSource(capsfilter1_src, inner_media_source.codec))

    def set_context(self, context):
        self.__context = context
        super(FilesaveMediaPoint, self).set_context(context)



