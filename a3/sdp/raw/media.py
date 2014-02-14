#!/usr/bin/env python
"""
sdp.raw.Media object
"""

import attribute
from entity import MediaDescription, MediaDescriptionProto, ConnectionData
from a3.media import MediaType


class Media(object):
    def __init__(self, media_type=MediaType.AUDIO, media_description=None):
        assert type(media_type) is MediaType
        assert media_description is None or type(media_description) is MediaDescription
        if media_description:
            self.__media_description = media_description
        else:
            self.__media_description = MediaDescription(media_type,
                                                        0,
                                                        MediaDescriptionProto.RTP_AVP,
                                                        [])
        self.__media_title = None
        self.__connection_data = None
        self.__bandwidths = []
        self.__encryption_key = None
        self.__attributes = attribute.AttributeCollection()

    @property
    def media_type(self):
        return self.__media_description.media_type

    @property
    def media_description(self):
        """

        :rtype : MediaDescription
        """
        return self.__media_description
    
    @media_description.setter
    def media_description(self, media_description):
        assert type(media_description) is MediaDescription
        self.__media_description = media_description

    @property
    def media_title(self):
        return self.__media_title

    @property
    def connection_data(self):
        return self.__connection_data
    
    @connection_data.setter
    def connection_data(self, connection_data):
        assert connection_data is None or type(connection_data) is ConnectionData
        self.__connection_data = connection_data

    @property
    def attributes(self):
        return self.__attributes

    @attributes.setter
    def attributes(self, attributes):
        assert type(attributes) is attribute.AttributeCollection
        self.__attributes = attributes

    def add_attribute(self, str_name, value=None):
        return self.__attributes.append(attribute.Attribute(str_name, value))

    def remove_attribute(self, attribute):
        return self.__attributes.remove(attribute)

    def to_str_list(self):
        lines = []
        lines.append("m=" + str(self.__media_description))                               # m=  (media name and transport address)
        if self.__media_title:       lines.append("i=" + str(self.__media_title))        # i=* (media title)
        if self.__connection_data:   lines.append("c=" + str(self.__connection_data))    # c=* (connection information)
        for b in self.__bandwidths:  lines.append("b=" + str(b))                         # b=* (zero or more bandwidth information lines)
        if self.__encryption_key:    lines.append("k=" + str(self.__encryption_key))     # k=* (encryption key)
        lines += self.__attributes.to_str_list()                                         # a=* (zero or more media attribute lines)
        return lines

    def __str__(self):
        return "\r\n".join(self.to_str_list()) + "\r\n"
