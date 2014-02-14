#!/usr/bin/env python
"""
http://tools.ietf.org/html/draft-ietf-mmusic-msid-00
Cross Session Stream Identification in the Session Description Protocol


a=ssrc:2981060093 cname:J6DFN5eAAZLoflul
a=ssrc:2981060093 msid:gOAmN6lzediz9H2WtqONgA9bbcmJldbeQDKf gOAmN6lzediz9H2WtqONgA9bbcmJldbeQDKfv0
a=ssrc:2981060093 mslabel:gOAmN6lzediz9H2WtqONgA9bbcmJldbeQDKf
a=ssrc:2981060093 label:gOAmN6lzediz9H2WtqONgA9bbcmJldbeQDKfv0

pc.LocalMediaStreams =
    [
        LocalMediaStream {
            id: "gOAmN6lzediz9H2WtqONgA9bbcmJldbeQDKf"
            label: "gOAmN6lzediz9H2WtqONgA9bbcmJldbeQDKf"
            audioTracks: [
                MediaStreamTrack {
                    enabled: true
                    id: "gOAmN6lzediz9H2WtqONgA9bbcmJldbeQDKfa0"
                    kind: "audio"
                    label: "Default"
                }
            ]
            videoTracks: [
                MediaStreamTrack {
                    id: "gOAmN6lzediz9H2WtqONgA9bbcmJldbeQDKfv0"
                    kind: "video"
                    label: "UVC Camera (046d:0809)"
            ]
        }
    ]

TODO: implement msid-semantic
"""


from raw.attribute import Attribute, AttributeCollection, SsrcValue
from raw.entity import MediaType
import error


class Stream(object):
    def __init__(self, ssrc_id, cname, msid=None, mslabel=None, label=None):
        assert type(ssrc_id) is long
        assert type(cname) is Attribute
        assert msid is None or type(msid) is Attribute
        assert mslabel is None or type(mslabel) is Attribute
        assert label is None or type(label) is Attribute

        self.__ssrc_id = ssrc_id
        self.__cname_attribute = cname
        self.__msid_attribute = msid
        self.__mslabel_attribute = mslabel
        self.__label_attribute = label

    @property
    def ssrc_id(self):
        return self.__ssrc_id

    @property
    def cname(self):
        return self.__cname_attribute.value.value

    @property
    def media_stream_label(self):
        return self.__mslabel_attribute.value.value if self.__mslabel_attribute else None

    @property
    def media_stream_track_label(self):
        return self.__label_attribute.value.value if self.__label_attribute else None

    @classmethod
    def from_attributes(cls, ssrc_id, attributes):
        assert type(ssrc_id) is long
        assert type(attributes) is AttributeCollection
        attrs = [a for a in attributes if a.name == "ssrc" and a.value.ssrc_id == ssrc_id]
        cnames = [a for a in attrs if a.value.attribute == "cname"]
        msids = [a for a in attrs if a.value.attribute == "msid"]
        mslabels = [a for a in attrs if a.value.attribute == "mslabel"]
        labels = [a for a in attrs if a.value.attribute == "label"]
        if len(cnames) != 1:
            raise error.SemanticError("Wrong number of CNAME attributes for " + ssrc_id)
        if len(msids) > 1:
            raise error.SemanticError("Wrong number of MSID attributes for " + ssrc_id)
        if len(mslabels) > 1:
            raise error.SemanticError("Wrong number of MSLABEL attributes for " + ssrc_id)
        if len(labels) > 1:
            raise error.SemanticError("Wrong number of LABEL attributes for " + ssrc_id)
        return cls(ssrc_id, cnames[0],
                   msids[0] if len(msids) == 1 else None,
                   mslabels[0] if len(mslabels) == 1 else None,
                   labels[0] if len(labels) == 1 else None)


class StreamCollection(object):
    def __init__(self, attributes):
        assert type(attributes) is AttributeCollection
        self.__attributes = attributes

        self.__streams = []

        ssrc_attributes = self.__attributes.get("ssrc")
        ssrc_ids = set([a.value.ssrc_id for a in ssrc_attributes])

        for ssrc_id in ssrc_ids:
            self.__streams.append(Stream.from_attributes(ssrc_id, attributes))

    @property
    def streams(self):
        return self.__streams

    def __nonzero__(self):
        return len(self.__streams) != 0

    def __getitem__(self, item):
        return self.__streams[item]

    def __len__(self):
        return len(self.__streams)

    def generate(self, ssrc_id=None, cname=None, stream_id=None, track_id=None, media_type=None):
        """
        TODO: this method is wrong and works only for one case - zero streams
        """
        assert ssrc_id is None or type(ssrc_id) is long
        assert cname is None or type(cname) is str
        assert stream_id is None or type(stream_id) is str
        assert track_id is None or type(track_id) is str

        if ssrc_id is None:
            ssrc_id = 1111L
        if cname is None:
            cname = "d7K1+bIOxM3hwrLB"
        if stream_id is None:
            stream_id = "OiLq8LkWFcq3I7yJSQOsSNpvHo8P4vZ3LT7K"
        if track_id is None:
            track_id = stream_id + "v0" if media_type is MediaType.VIDEO else stream_id + "a0"

        stream_label = stream_id
        track_label = track_id

        cname_attribute = Attribute("ssrc", SsrcValue(ssrc_id, "cname", cname))
        msid_attribute = Attribute("ssrc", SsrcValue(ssrc_id, "msid", stream_id + " " + track_id))
        mslabel_attribute = Attribute("ssrc", SsrcValue(ssrc_id, "mslabel", stream_label))
        label_attribute = Attribute("ssrc", SsrcValue(ssrc_id, "label", track_label))
        self.__attributes.append(cname_attribute)
        self.__attributes.append(msid_attribute)
        self.__attributes.append(mslabel_attribute)
        self.__attributes.append(label_attribute)
        stream = Stream(ssrc_id,
                        cname_attribute,
                        msid_attribute,
                        mslabel_attribute,
                        label_attribute)
        self.__streams.append(stream)


if __name__ == "__main__":
    import unittest

    def create_attributes1():
        return AttributeCollection([
            Attribute("ssrc", SsrcValue(1L, "cname", "stream1")),
            Attribute("ssrc", SsrcValue(1L, "mslabel", "stream1")),
            Attribute("ssrc", SsrcValue(1L, "label", "audiotrack0"))
        ])

    class StreamTest(unittest.TestCase):
        def test_init(self):
            attributes = create_attributes1()
            stream = Stream.from_attributes(1L, attributes)
            self.failUnlessEqual(stream.ssrc_id, 1L)
            self.failUnlessEqual(stream.cname, "stream1")
            self.failUnlessEqual(stream.media_stream_label, "stream1")
            self.failUnlessEqual(stream.media_stream_track_label, "audiotrack0")

    unittest.main()
