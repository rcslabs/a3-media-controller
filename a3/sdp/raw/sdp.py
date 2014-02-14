#!/usr/bin/env python
"""
SDP



TODO: As per the latest draft when you use BUNDLE in offer/answer than rtcp-mux attribute must be specified.
In your case you are using BUNDLE in answer without rtcp-mux. Please refer to section 6.1 in the below draft.



"""


import attribute
import entity
import attributes.error
import media


ParseError = attributes.error.ParseError


#
# https://groups.google.com/forum/?fromgroups=#!topic/discuss-webrtc/zbOWzeqfobs
#
#Chrome uses the "1" initial version number in the o= line as an indication of an older version that can only do GICE.
# Change that to 2, e.g.
#o=- 1348104409651 2 IN IP4 127.0.0.1
#
#Yes, starting the session version at 2 makes the behavior of both PCs consistently rfc 5245 style.
#


class Sdp(object):

    def __init__(self):
        self.__protocol_version = entity.ProtocolVersion(0)
        self.__origin_value = entity.Origin("-", "0", "0", entity.NetType.IN, entity.AddrType.IP4, "127.0.0.1")
        self.__session_name = entity.SessionName("Session SIP/SDP")
        self.__session_information = None
        self.__uri = None
        self.__email_address = None
        self.__phone_number = None
        self.__connection_data = None
        self.__bandwidths = []
        self.__time_descriptions = [entity.TimeDescription(entity.Timing(0L, 0L))]
        self.__time_zones = None
        self.__encryption_key = None
        self.__attributes = attribute.AttributeCollection()
        self.__medias = []

    @property
    def protocol_version(self):
        return self.__protocol_version

    @protocol_version.setter
    def protocol_version(self, protocol_version):
        assert type(protocol_version) is entity.ProtocolVersion
        self.__protocol_version = protocol_version

    @property
    def origin_value(self):
        return self.__origin_value

    @origin_value.setter
    def origin_value(self, origin_value):
        assert type(origin_value) is entity.Origin
        self.__origin_value = origin_value

    @property
    def session_name(self):
        return self.__session_name

    @session_name.setter
    def session_name(self, session_name):
        assert type(session_name) is entity.SessionName
        self.__session_name = session_name

    @property
    def session_information(self):
        return self.__session_information

    @session_information.setter
    def session_information(self, session_information):
        assert type(session_information) is entity.SessionInformation
        self.__session_information = session_information
    
    # uri
    
    # email_address
    
    # phone_number
    
    @property
    def connection_data(self):
        return self.__connection_data
    
    @connection_data.setter
    def connection_data(self, connection_data):
        assert type(connection_data) is entity.ConnectionData
        self.__connection_data = connection_data

    # bandwidths
    
    # time_descriptions
    @property
    def time_descriptions(self):
        return self.__time_descriptions

    @time_descriptions.setter
    def time_descriptions(self, time_descriptions):
        self.__time_descriptions = time_descriptions

    # time_zones
    # encryption_key

    @property
    def medias(self):
        return self.__medias

    def add_media(self, raw_media):
        assert type(raw_media) is media.Media
        self.__medias.append(raw_media)

    def add_attribute(self, str_name, value=None):
        return self.__attributes.set(str_name, value)

    @property
    def attributes(self):
        return self.__attributes

    @attributes.setter
    def attributes(self, val):
        assert type(val) is attribute.AttributeCollection
        self.__attributes = val

    def to_str_list(self):
        lines = []
        lines.append("v=" + str(self.__protocol_version))                                               # v=  (protocol version)
        lines.append("o=" + str(self.__origin_value))                                                   # o=  (originator and session identifier)
        lines.append("s=" + str(self.__session_name))                                                   # s=  (session name)
        if self.__session_information       : lines.append("i=" + str(self.__session_information))      # i=* (session information)
        if self.__uri                       : lines.append("u=" + str(self.__uri))                      # u=* (URI of description)
        if self.__email_address             : lines.append("e=" + str(self.__email_address))            # e=* (email address)
        if self.__phone_number              : lines.append("p=" + str(self.__phone_number))             # p=* (phone number)
        if self.__connection_data           : lines.append("c=" + str(self.__connection_data))          # c=* (connection information)
        for b in self.__bandwidths          : lines.append("b=" + str(b))                               # b=* (zero or more bandwidth information lines)
        for t in self.__time_descriptions   : lines += t.to_str_list()                                  # One or more time descriptions ("t=" and "r=" lines)
        if self.__time_zones                : lines.append("z=" + str(self.__time_zones))               # z=* (time zone adjustments)
        if self.__encryption_key            : lines.append("k=" + str(self.__encryption_key))           # k=* (encryption key)
        lines += self.__attributes.to_str_list()                                                        # a=* (zero or more session attribute lines)
        for media in self.__medias          : lines += media.to_str_list()                              # Zero or more media descriptions
        return lines

    def __str__(self):
        return '\r\n'.join(self.to_str_list()) + '\r\n'


if __name__ == "__main__":
    import unittest
    unittest.main()

