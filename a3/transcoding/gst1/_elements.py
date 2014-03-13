#!/usr/bin/env python
"""
Gstreamer-1 elements
"""


from ...logging import LOG
from .._base import ITranscodingContext
from ._socket import Socket


from string import Template
from ._base import Gst


WIDTH = 640
HEIGHT = 480
FRAMERATE = 15


VP8_ENCODE = Template("""queue !
                         videorate max-rate=30 !
                         video/x-raw,framerate=(fraction)$framerate/1 !
                         videoscale !
                         video/x-raw,framerate=(fraction)$framerate/1,width=(int)$width,height=(int)$height !
                         vp8enc keyframe-max-dist=300 end-usage=cbr deadline=1
                                undershoot=100 overshoot=100
                                target-bitrate=500000 cpu-used=4 threads=3 error-resilient=1 !
                         queue max-size-time=0""")

H264_ENCODE = Template("""queue !
                          videorate ! videoscale !
                          video/x-raw,framerate=(fraction)$framerate/1,width=(int)$width,height=(int)$height !
                          x264enc byte-stream=true bitrate=500 pass=pass1 speed-preset=1""")

H263_1998_ENCODE = Template("""queue !
                            videorate max-rate=30 ! videoscale !
                            video/x-raw,framerate=(fraction)$framerate/1,width=(int)$width,height=(int)$height !
                            avenc_h263p""")

PCMA_ENCODE = Template("""queue !
                          alawenc""")

SRC_PAD_NAME = 'src_%u'
SEND_RTP_SINK_PAD = "send_rtp_sink_%u"

VIDEO_TEST_SRC = "videotestsrc pattern=18 ! video/x-raw,framerate=(fraction)15/1,width=(int)352,height=(int)288 ! queue"

AUDIO_TEST_SRC = "audiotestsrc ! audioconvert ! queue"

RTPBIN = "rtpbin"

# TODO:
#  tcpclientsrc port=8554 host=localhost ! gdpdepay ! application/x-rtp, payload=96 !


class GstElement(object):
    def __init__(self, element):
        assert element
        self._element = element

    @property
    def element(self):
        """
         Returns gst element or bin
        """
        assert self._element
        return self._element

    def link(self, next_):
        assert self._element
        assert issubclass(type(next_), GstElement)
        self._element.link(next_._element)

    def get_pad(self, pad_name):
        assert self._element
        assert type(pad_name) is str
        pad = self._element.get_static_pad(pad_name)
        assert pad
        return pad

    #def unlink(self, next=None):
    #    assert(next is None or issubclass(type(next), GstElement))
    #    self._element.unlink(next)

    @property
    def sink_pad(self):
        return self.get_pad("sink")

    @property
    def src_pad(self):
        return self.get_pad("src")

    def get_property(self, property_name):
        assert self._element
        return self._element.get_property(property_name)

    def play(self):
        assert self._element
        self._element.set_state(Gst.State.PLAYING)

    def pause(self):
        assert self._element
        self._element.set_state(Gst.State.PAUSED)

    def stop(self):
        assert self._element
        self._element.set_state(Gst.State.NULL)

    def dispose(self):
        assert self._element
        self._element.set_state(Gst.State.NULL)
        del self._element


class GstBin(GstElement):
    def __init__(self, str_template=None):
        assert str_template is None or type(str_template) is str
        super(GstBin, self).__init__(Gst.parse_bin_from_description(str_template, True) if str_template else Gst.Bin())

    def add(self, gst_element):
        assert isinstance(gst_element, GstElement)
        self._element.add(gst_element._element)
        gst_element._element.sync_state_with_parent()

    def remove(self, gst_element):
        assert isinstance(gst_element, GstElement)
        self._element.remove(gst_element._element)


#
# Src
#
class VideoTestSrc(GstElement):
    def __init__(self):
        super(VideoTestSrc, self).__init__(Gst.parse_bin_from_description(VIDEO_TEST_SRC, True))


class AudioTestSrc(GstElement):
    def __init__(self):
        super(AudioTestSrc, self).__init__(Gst.parse_bin_from_description(AUDIO_TEST_SRC, True))


class UdpSrc(GstElement):
    def __init__(self, socket):
        assert type(socket) is Socket
        super(UdpSrc, self).__init__(Gst.ElementFactory.make('udpsrc', None))
        self._element.set_property("socket", socket.socket)
        self._element.set_property("close-socket", False)
        self._element.set_state(Gst.State.PAUSED)

    def set_caps(self, str_caps):
        self._element.set_property("caps", Gst.caps_from_string(str_caps))

    @property
    def port(self):
        return self._element.get_property("port")

    def __str__(self):
        return "[UdpSrc, port: {0}]".format(self.port)


#
# Sink
#
class FakeSink(GstElement):
    def __init__(self):
        #fakesink sync=true async=false
        super(FakeSink, self).__init__(Gst.ElementFactory.make("fakesink", None))
        self._element.set_property("sync", True)


class DebugPrintSink(GstElement):
    def __init__(self):
        LOG.info("Creating DebugPrint Sink")
        super(DebugPrintSink, self).__init__(Gst.Bin())
        self.__fakesink = Gst.ElementFactory.make("fakesink", None)
        self.__fakesink.set_property("dump", "true")

        self._element.add(self.__fakesink)

        sink_pad = self.__fakesink.get_static_pad("sink")
        bin_sink_pad = Gst.GhostPad.new("sink", sink_pad)
        self._element.add_pad(bin_sink_pad)


class UdpSink(GstElement):
    """
        udpsink sync=false async=false host="127.0.0.1" port=0
    """
    def __init__(self, port=0, host="127.0.0.1", socket=None):
        super(UdpSink, self).__init__(Gst.ElementFactory.make("udpsink", None))
        self._element.set_property("sync", False)
        self._element.set_property("async", False)
        self._element.set_property("port", port)
        self._element.set_property("host", host)
        if socket:
            assert type(socket) is Socket
            self._element.set_property("socket", socket.socket)

    def set_destination(self, destination_port=0, destination_host="127.0.0.1"):
        self._element.set_property("port", destination_port)
        self._element.set_property("host", destination_host)


class RtpBin(GstElement):
    def __init__(self, pad_added=None, request_pt_map=None):
        super(RtpBin, self).__init__(Gst.ElementFactory.make(RTPBIN, None))
        self.__rtp_io = None

        def rtpbin_ssrc_sdes(rtpbin, sessid, ssrc):
            session = rtpbin.emit("get-internal-session", sessid)
            source = session.emit("get-source-by-ssrc", ssrc)
            sdes = source.get_property("sdes")
            cname = sdes.get_value("cname")
            LOG.info("rtpbin :: on-ssrc-sdes CNAME=%s, SSRC=%s", repr(cname), repr(ssrc))

        #def rtpbin_pad_added(_, pad):
        #    pass
        #    #pad_name = pad.get_property("name")
        #    #LOG.info("PAD_ADDED %s", repr(pad_name))

        def rtpbin_new_ssrc(rtpbin, session, ssrc):
            LOG.debug("rtpbin::on-new-ssrc %d", ssrc)

        def rtpbin_ssrc_active(_, a, b):
            #print "rtpbin_ssrc_active", a, b
            #print "PADS =", map(lambda pad: pad.get_name(), self._element.pads)
            pass

        def rtpbin_ssrc_validated(rtpbin, _, ssrc):
            #print "on_ssrc_validated", rtpbin, _, ssrc
            pass

        #bus = self.__rtpbin.get_bus()
        #print "BUS=", repr(bus)

        self._element.connect("on-new-ssrc", rtpbin_new_ssrc)
        self._element.connect("on-ssrc-sdes", rtpbin_ssrc_sdes)
        self._element.connect("on-ssrc-active", rtpbin_ssrc_active)
        self._element.connect("on-ssrc-validated", rtpbin_ssrc_validated)
        if pad_added:
            self._element.connect("pad-added", pad_added, self)
        if request_pt_map:
            self._element.connect("request-pt-map", request_pt_map, self)

        sink_pad = self._element.get_request_pad(SEND_RTP_SINK_PAD)
        assert sink_pad
        #bin_sink_pad = Gst.GhostPad.new("sink", sink_pad)
        #self._element.add_pad(bin_sink_pad)

    @property
    def rtp_socket(self):
        return self.__rtp_io.rtp_socket

    @property
    def rtcp_socket(self):
        return self.__rtp_io.rtcp_socket

    def __get_sdes(self, property_name):
        """
        get source description property
        can be:
        "cname", "name", "email", "phone", "location", "tool", "note", "session"
        """
        sdes = self._element.get_property("sdes")
        return sdes.get_value(property_name)

    @property
    def cname(self):
        sdes = self._element.get_property("sdes")
        return sdes.get_value("cname")

    @cname.setter
    def cname(self, cname):
        assert type(cname) is str
        sdes = self._element.get_property("sdes")
        sdes.set_value("cname", cname)
        self._element.set_property("sdes", sdes)

    @property
    def ssrc(self):
        session = self._element.emit("get-internal-session", 0)
        assert session
        ssrc = session.get_property("internal-ssrc")
        assert (type(ssrc) is long) or (type(ssrc) is int)
        assert (type(ssrc) is long) or (type(ssrc) is int)
        return long(ssrc)

    @ssrc.setter
    def ssrc(self, ssrc):
        assert type(ssrc) is long
        session = self._element.emit("get-internal-session", 0)
        assert session
        session.set_property("internal-ssrc", ssrc)


class TeeWrapper(GstElement):
    def __init__(self):
        super(TeeWrapper, self).__init__(Gst.ElementFactory.make("tee", None))
        self.__next_elements = []

    def link(self, next_):
        assert issubclass(type(next_), GstElement)
        src_pad = self._element.get_request_pad(SRC_PAD_NAME)
        assert src_pad
        LOG.debug("Adding tee pad: %s", src_pad.get_property("name"))
        src_pad.link(next_._element.get_static_pad("sink"))
        self.__next_elements.append((src_pad, next_))

    def unlink(self, next_):
        assert issubclass(type(next_), GstElement)
        src_pad = self.__find_pad(next_)
        if src_pad is None:
            LOG.warn("Tee: no element %s", repr(next_))
            return

        LOG.debug("Removing tee pad %s", src_pad.get_property("name"))
        self.__next_elements.remove((src_pad, next_))
        src_pad.set_active(False)
        src_pad.unlink(next_._element.get_static_pad('sink'))
        self._element.remove_pad(src_pad)
        #next_.set_state(Gst.State.PAUSED)

    def __find_pad(self, next_):
        for (pad, el) in self.__next_elements:
            if el is next_:
                return pad
        return None


class FakeEncoder(GstElement):
    def __init__(self):
        super(FakeEncoder, self).__init__(Gst.ElementFactory.make("queue", None))


#
# depay
#

class PCMADepay(GstElement):
    def __init__(self):
        super(PCMADepay, self).__init__(Gst.ElementFactory.make("rtppcmadepay", None))


class H264Depay(GstElement):
    def __init__(self):
        super(H264Depay, self).__init__(Gst.ElementFactory.make("rtph264depay", None))


class VP8Depay(GstElement):
    def __init__(self):
        super(VP8Depay, self).__init__(Gst.ElementFactory.make("rtpvp8depay", None))


class H263_1998Depay(GstElement):
    def __init__(self):
        super(H263_1998Depay, self).__init__(Gst.ElementFactory.make("rtph263pdepay", None))


#
# pay
#

class PCMAPay(GstElement):
    def __init__(self, ssrc_id, payload_type):
        """rtppcmapay ssrc=$ssrc pt=$pt mtu=172"""
        assert type(ssrc_id) is long
        assert type(payload_type) is int
        super(PCMAPay, self).__init__(Gst.ElementFactory.make("rtppcmapay", None))
        self._element.set_property("ssrc", ssrc_id)
        self._element.set_property("pt", payload_type)
        self._element.set_property("mtu", 172)


class H264Pay(GstElement):
    def __init__(self, ssrc_id, payload_type):
        """rtph264pay ssrc=$ssrc pt=$pt"""
        assert type(ssrc_id) is long
        assert type(payload_type) is int
        super(H264Pay, self).__init__(Gst.ElementFactory.make("rtph264pay", None))
        self._element.set_property("ssrc", ssrc_id)
        self._element.set_property("pt", payload_type)


class VP8Pay(GstElement):
    def __init__(self, ssrc_id, payload_type):
        """rtpvp8pay ssrc=$ssrc pt=$pt mtu=1400"""
        assert type(ssrc_id) is long
        assert type(payload_type) is int
        super(VP8Pay, self).__init__(Gst.ElementFactory.make("rtpvp8pay", None))
        self._element.set_property("ssrc", ssrc_id)
        self._element.set_property("pt", payload_type)
        self._element.set_property("mtu", 1400)


class H263_1998Pay(GstElement):
    def __init__(self, ssrc_id, payload_type):
        """rtph263ppay ssrc=$ssrc pt=$pt"""
        assert type(ssrc_id) is long
        assert type(payload_type) is int
        super(H263_1998Pay, self).__init__(Gst.ElementFactory.make("rtph263ppay", None))
        self._element.set_property("ssrc", ssrc_id)
        self._element.set_property("pt", payload_type)


#
# encoder
#
class Encoder(GstBin):
    def __init__(self, str_template):
        assert type(str_template) is str
        super(Encoder, self).__init__(str_template)


class VideoEncoder(Encoder):
    def __init__(self, template):
        super(VideoEncoder, self).__init__(template.substitute(dict(width=WIDTH, height=HEIGHT, framerate=FRAMERATE)))


class AudioEncoder(Encoder):
    def __init__(self, template):
        super(AudioEncoder, self).__init__(template.substitute(dict()))


class VP8Encoder(VideoEncoder):
    def __init__(self):
        super(VP8Encoder, self).__init__(VP8_ENCODE)


class H264Encoder(VideoEncoder):
    def __init__(self):
        super(H264Encoder, self).__init__(H264_ENCODE)


class H263_1998Encoder(VideoEncoder):
    def __init__(self):
        super(H263_1998Encoder, self).__init__(H263_1998_ENCODE)


class PCMAEncoder(AudioEncoder):
    def __init__(self):
        super(PCMAEncoder, self).__init__(PCMA_ENCODE)


#
# decoder
#
class Decoder(GstElement):
    pass


class VP8Decoder(Decoder):
    def __init__(self):
        """vp8dec"""
        super(VP8Decoder, self).__init__(Gst.ElementFactory.make("vp8dec", None))


class H264Decoder(Decoder):
    def __init__(self):
        """avdec_h264"""
        super(H264Decoder, self).__init__(Gst.ElementFactory.make("avdec_h264", None))


class H263_1998Decoder(Decoder):
    def __init__(self):
        """avdec_h263"""
        super(H263_1998Decoder, self).__init__(Gst.ElementFactory.make("avdec_h263", None))


class PCMADecoder(Decoder):
    def __init__(self):
        """alawdec ! audioconvert ! audioresample"""
        super(PCMADecoder, self).__init__(Gst.parse_bin_from_description("""alawdec ! audioconvert ! audioresample""",
                                                                         True))


class GstPipeline(GstElement, ITranscodingContext):
    def __init__(self):
        super(GstPipeline, self).__init__(Gst.Pipeline())

    def add(self, gst_element):
        assert isinstance(gst_element, GstElement)
        self._element.add(gst_element._element)
        gst_element._element.sync_state_with_parent()

    def remove(self, gst_element):
        assert isinstance(gst_element, GstElement)
        self._element.remove(gst_element._element)

    def dispose(self):
        super(GstPipeline, self).dispose()
