#!/usr/bin/env python
"""
declare MediaType

MediaType may be:
    audio
    video
    application
    message

Now supported only audio and video
"""

__author__ = 'RCSLabs'


class _MediaTypeMetaTemp(type):
    AUDIO = None
    VIDEO = None


class MediaType(str):
    __metaclass__ = _MediaTypeMetaTemp

    @classmethod
    def from_string(cls, string):
        assert type(string) is str
        if string == "audio":
            return _MediaTypeMeta.AUDIO
        elif string == "video":
            return _MediaTypeMeta.VIDEO
        #else:
        #    raise ParseError("MediaType is " + repr(string))


class _MediaTypeMeta(type):
    AUDIO = MediaType("audio")
    VIDEO = MediaType("video")


MediaType.__class__ = _MediaTypeMeta


if __name__ == "__main__":
    import unittest

    class MediaTypeTest(unittest.TestCase):
        def test_init(self):
            assert type(MediaType.AUDIO) is MediaType
            assert type(MediaType.VIDEO) is MediaType
            try:
                MediaType.AUDIO.AUDIO
                self.fail("MediaType.AUDIO.AUDIO")
            except AttributeError:
                pass

    unittest.main()
