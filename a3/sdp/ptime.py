#!/usr/bin/env python


from raw.attribute import Attribute, AttributeCollection, PtimeValue


class Ptime(object):
    def __init__(self, attributes):
        assert type(attributes) is AttributeCollection
        self.__attributes = attributes
        ptimes = attributes.get("ptime")
        assert len(ptimes) < 2
        self.__ptime_attribute = ptimes[0] if len(ptimes) == 1 else None

    def __nonzero__(self):
        return self.__ptime_attribute is not None

    @property
    def packet_time(self):
        return self.__ptime_attribute.value.packet_time if self.__ptime_attribute else None

    @packet_time.setter
    def packet_time(self, packet_time):
        assert packet_time is None or type(packet_time) is int
        if packet_time is not None:
            self.__set_packet_time(packet_time)
        else:
            self.__remove_packet_time()

    def __set_packet_time(self, packet_time):
        assert type(packet_time) is int
        if self.__ptime_attribute is not None:
            self.__ptime_attribute.value.packet_time = packet_time
        else:
            self.__ptime_attribute = Attribute("ptime", PtimeValue(packet_time))
            self.__attributes.append(self.__ptime_attribute)

    def __remove_packet_time(self):
        if self.__ptime_attribute is not None:
            self.__ptime_attribute.remove()
            self.__ptime_attribute = None

