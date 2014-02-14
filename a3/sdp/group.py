#!/usr/bin/env python


from raw.attribute import GroupSemanticsValue, GroupSemantics, Attribute, Group as RawGroup
import session_description
from error import SemanticError


def generate_name(prefix, reserved_names):
    i = 0
    name = prefix
    while name in reserved_names:
        i += 1
        name = prefix + "-" + str(i)
    reserved_names.append(name)
    return name


class Group(object):
    def __init__(self, sdp):
        assert type(sdp) is session_description.SessionDescription
        groups = sdp.raw_sdp.attributes.get("group")
        if len(groups) >= 1:
            raise SemanticError("More then one crypto in SDP")
        self.__sdp = sdp
        self.__attribute = groups[0] if len(groups) == 1 else None

    @property
    def semantics(self):
        return self.__attribute.value.semantics if self.__attribute else None

    @semantics.setter
    def semantics(self, semantics):
        assert semantics is None or type(semantics) is GroupSemanticsValue
        if semantics is None:
            self.__remove_attribute()
        else:
            self.__add_attribute(semantics)

    def __remove_attribute(self):
        if self.__attribute is not None:
            self.__attribute.remove()
            self.__attribute = None

    def __add_attribute(self, semantics):
        mids = self.__get_mids()
        if self.__attribute is None:
            self.__attribute = Attribute("group", RawGroup(semantics, mids))
            self.__sdp.raw_sdp.attributes.append(self.__attribute)

    def __get_mids(self):
        reserved_mids = [media.mid for media in self.__sdp.medias if media.mid is not None]
        mids = []
        for media in self.__sdp.medias:
            if media.mid is not None:
                mids.append(media.mid)
            else:
                new_mid = generate_name(str(media.media_type), reserved_mids)
                media.mid = new_mid
                mids.append(new_mid)
        return mids

    def add_media(self, media):
        if self.__attribute:
            mids = [media.mid for media in self.__sdp.medias if media.mid is not None]
            new_mid = generate_name(str(media.media_type), mids)
            media.mid = new_mid
            self.__attribute.value.identification_tags.append(new_mid)

if __name__ == "__main__":
    import unittest
    from raw.media import Media as RawMedia, MediaType

    class GenerateNameTest(unittest.TestCase):
        def test_0(self):
            self.failUnlessEqual("audio", generate_name("audio", []))
            self.failUnlessEqual("audio-1", generate_name("audio", ["audio"]))
            self.failUnlessEqual("audio-1", generate_name("audio", ["audio", "audio-0"]))
            self.failUnlessEqual("audio-2", generate_name("audio", ["audio", "audio-1"]))
            self.failUnlessEqual("audio-2", generate_name("audio", ["audio", "audio-3", "audio-1"]))

    class GroupTest(unittest.TestCase):
        def test_set(self):
            sdp = session_description.SessionDescription()
            sdp.add_raw_media(RawMedia(MediaType.VIDEO))
            sdp.add_raw_media(RawMedia(MediaType.VIDEO))
            sdp.add_raw_media(RawMedia(MediaType.AUDIO))
            sdp.group_semantics = GroupSemantics.BUNDLE
            self.failUnlessEqual(sdp.medias[0].mid, "video")
            self.failUnlessEqual(sdp.medias[1].mid, "video-1")
            self.failUnlessEqual(sdp.medias[2].mid, "audio")
            self.failUnlessEqual(str(sdp.raw_sdp.attributes[0]), "group:BUNDLE video video-1 audio")
            sdp.group_semantics = None
            self.failUnlessEqual(len(sdp.raw_sdp.attributes), 0)

        def test_add(self):
            sdp = session_description.SessionDescription()
            sdp.group_semantics = GroupSemantics.BUNDLE
            sdp.add_raw_media(RawMedia(MediaType.VIDEO))
            sdp.add_raw_media(RawMedia(MediaType.VIDEO))
            sdp.add_raw_media(RawMedia(MediaType.AUDIO))
            self.failUnlessEqual(sdp.medias[0].mid, "video")
            self.failUnlessEqual(sdp.medias[1].mid, "video-1")
            self.failUnlessEqual(sdp.medias[2].mid, "audio")
            self.failUnlessEqual(str(sdp.raw_sdp.attributes[0]), "group:BUNDLE video video-1 audio")


    unittest.main()