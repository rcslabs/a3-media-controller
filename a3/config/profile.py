#!/usr/bin/env python


import re
import collections
import random
import logging


DEFAULT_MIN_PORT = 1024
DEFAULT_MAX_PORT = 65535
DEFAULT_IP = "127.0.0.1"
DEFAULT_INTERFACE = "0.0.0.0"


class ProfileError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class _Range(object):
    """
    a class for iterating (even, odd) pairs
    """

    def __init__(self, start, end):
        assert type(start) is int
        assert type(end) is int
        if not (1 <= start <= DEFAULT_MAX_PORT):
            raise ProfileError("Port %d is out of range" % start)
        if not (1 <= end <= DEFAULT_MAX_PORT):
            raise ProfileError("Port %d is out of range" % end)
        if not start < end:
            raise ProfileError("Port %d is not less then %d" % (start, end))
        self.__start = start
        self.__end = end

    def __len__(self):
        return (self.__end - self.__start - self.__start % 2) / 2

    def __cmp__(self, other):
        if self.__start == other.start and self.__end == other.end:
            return 0
        elif self.__start == other.start:
            return self.__end - other.end
        else:
            return self.__start - other.start

    def __contains__(self, n):
        assert isinstance(n, collections.Iterable) and len(n) == 2
        rtp, rtcp = n
        assert (type(rtp) is int) and (type(rtcp) is int) and (rtp + 1 == rtcp) and (rtp % 2 == 0)
        return self.__start <= rtp < rtcp < self.__end

    def __str__(self):
        return "%d-%d" % (self.__start, self.__end)

    def __iter__(self):
        offset = random.randrange(len(self))
        return self.offset_iterator(offset)

    def offset_iterator(self, offset=0):
        assert type(offset) is int
        l = len(self)
        for i in xrange(0, l):
            yield self[(offset + i) % l]

    @property
    def start(self):
        return self.__start

    @property
    def end(self):
        return self.__end

    def __getitem__(self, key):
        if type(key) is not int:
            raise TypeError()
        if not 0 <= key < len(self):
            raise IndexError()
        rtp_port = self.__start + (self.__start % 2) + key * 2
        return rtp_port, rtp_port + 1


class _RangeAny(_Range):
    def __init__(self):
        super(_RangeAny, self).__init__(DEFAULT_MIN_PORT, DEFAULT_MAX_PORT)

    def __str__(self):
        return "*"


class Profile(object):
    def __init__(self, profile_str, default_ip=DEFAULT_IP):
        assert type(profile_str) is str
        assert type(default_ip) is str

        g = re.match("^(\d+\.\d+\.\d+\.\d+)?(?:(?::|^)(\*|(?:(\d+)-(\d+))))?(?:\s*\((\d+\.\d+\.\d+\.\d+)\))?$",
                     profile_str)
        if not g:
            raise ProfileError("Cannot parse Profile string: %s" % profile_str)
        self.__ip = g.group(1) if g and g.group(1) else default_ip
        self.__ports_range = _Range(int(g.group(3)), int(g.group(4))) if g and g.group(2) and g.group(2) != "*" \
            else _RangeAny()
        self.__interface = g.group(5) if g and g.group(5) else DEFAULT_INTERFACE

    @property
    def ip(self):
        return self.__ip

    @property
    def ports_range(self):
        return self.__ports_range

    @property
    def interface(self):
        return self.__interface

    def __str__(self):
        return "%s:%s (interface=%s)" % (self.__ip, self.__ports_range, self.__interface)


if __name__ == "__main__":
    FORMAT = '%(asctime)-15s %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.DEBUG)

    import unittest

    class RangeTest(unittest.TestCase):
        def test_init(self):
            self.failUnlessRaises(AssertionError, _Range, 0L, None)
            self.failUnlessRaises(AssertionError, _Range, 0L, 1L)
            self.failUnlessRaises(AssertionError, _Range, None, "x")
            self.failUnlessRaises(ProfileError, _Range, 1, 1)
            self.failUnlessRaises(ProfileError, _Range, 10, 1)
            self.failUnlessRaises(ProfileError, _Range, 0, 65536)
            self.failUnlessEqual(_Range(1, 100).start, 1)
            self.failUnlessEqual(_Range(1, 100).end, 100)
            self.failUnlessEqual(_Range(15, 16).end, 16)

        def test_compare(self):
            self.failUnless(_Range(1, 100) < _Range(2, 100))
            self.failUnless(_Range(2, 99) < _Range(2, 100))
            self.failUnless(_Range(2, 100) > _Range(1, 100))
            self.failUnless(_Range(2, 100) > _Range(2, 99))
            self.failUnless(_Range(1, 100) <= _Range(2, 100))
            self.failUnless(_Range(2, 99) <= _Range(2, 100))
            self.failUnless(_Range(2, 100) >= _Range(1, 100))
            self.failUnless(_Range(2, 100) >= _Range(2, 99))
            self.failUnless(_Range(2, 5) == _Range(2, 5))
            self.failUnless(_Range(2, 5) >= _Range(2, 5))
            self.failUnless(_Range(2, 5) <= _Range(2, 5))

        def test_sort(self):
            lst = [_Range(1, 100), _Range(3, 100), _Range(2, 100),
                   _Range(3, 101), _Range(1, 101), _Range(2, 101),
                   _Range(1, 102), _Range(2, 102), _Range(3, 102)]
            lst.sort()
            self.failUnlessEqual(lst,
                                 [_Range(1, 100), _Range(1, 101), _Range(1, 102),
                                  _Range(2, 100), _Range(2, 101), _Range(2, 102),
                                  _Range(3, 100), _Range(3, 101), _Range(3, 102)])

        def test_contains(self):
            self.failUnlessRaises(AssertionError, lambda: (1, 2) in _Range(1, 20))
            self.failUnlessRaises(AssertionError, lambda: (1, 3) in _Range(1, 20))
            self.failUnlessRaises(AssertionError, lambda: (4, 3) in _Range(1, 20))
            self.failUnlessRaises(AssertionError, lambda: (5, 4) in _Range(1, 20))
            self.failUnless((2, 3) in _Range(1, 10))
            self.failUnless((4, 5) in _Range(1, 10))
            self.failUnless((8, 9) in _Range(1, 10))
            self.failIf((0, 1) in _Range(1, 10))
            self.failIf((10, 11) in _Range(1, 10))
            self.failIf((10, 11) in _Range(1, 11))

        def test_len(self):
            self.failUnlessEqual(len(_Range(1, 2)), 0)
            self.failUnlessEqual(len(_Range(1, 3)), 0)
            self.failUnlessEqual(len(_Range(1, 4)), 1)              # (2,3)
            self.failUnlessEqual(len(_Range(1, 5)), 1)
            self.failUnlessEqual(len(_Range(1, 6)), 2)              # (2,3), (4,5)
            self.failUnlessEqual(len(_Range(1, 7)), 2)
            self.failUnlessEqual(len(_Range(1, 8)), 3)              # (2,3), (4,5), (6,7)
            self.failUnlessEqual(len(_Range(1, 9)), 3)
            self.failUnlessEqual(len(_Range(2, 3)), 0)
            self.failUnlessEqual(len(_Range(2, 4)), 1)
            self.failUnlessEqual(len(_Range(2, 5)), 1)
            self.failUnlessEqual(len(_Range(2, 6)), 2)
            self.failUnlessEqual(len(_Range(2, 7)), 2)
            self.failUnlessEqual(len(_Range(2, 8)), 3)              # (2,3), (4,5), (6,7)
            self.failUnlessEqual(len(_Range(2, 9)), 3)

        def test_iterator(self):
            self.failUnlessEqual(list(_Range(1, 5)), [(2, 3)])
            self.failUnlessEqual(list(_Range(1, 10)), [(2, 3), (4, 5), (6, 7), (8, 9)])
            self.failUnlessEqual(list(_Range(2, 5)), [(2, 3)])
            self.failUnlessEqual(list(_Range(2, 10)), [(2, 3), (4, 5), (6, 7), (8, 9)])

        def test_offset_iterator(self):
            self.failUnlessEqual(list(_Range(1, 5).offset_iterator(0)), [(2, 3)])
            self.failUnlessEqual(list(_Range(1, 5).offset_iterator(1)), [(2, 3)])
            self.failUnlessEqual(list(_Range(1, 10).offset_iterator(0)), [(2, 3), (4, 5), (6, 7), (8, 9)])
            self.failUnlessEqual(list(_Range(1, 10).offset_iterator(1)), [(4, 5), (6, 7), (8, 9), (2, 3)])
            self.failUnlessEqual(list(_Range(1, 10).offset_iterator(2)), [(6, 7), (8, 9), (2, 3), (4, 5)])
            self.failUnlessEqual(list(_Range(1, 10).offset_iterator(3)), [(8, 9), (2, 3), (4, 5), (6, 7)])
            self.failUnlessEqual(list(_Range(1, 10).offset_iterator(4)), [(2, 3), (4, 5), (6, 7), (8, 9)])
            self.failUnlessEqual(list(_Range(2, 5).offset_iterator(0)), [(2, 3)])
            self.failUnlessEqual(list(_Range(2, 10).offset_iterator(0)), [(2, 3), (4, 5), (6, 7), (8, 9)])

        def test_get_item(self):
            r = _Range(2, 10)
            self.failUnlessEqual(r[0], (2, 3))
            self.failUnlessEqual(r[1], (4, 5))

    class ProfileTest(unittest.TestCase):
        def test_init(self):
            self.failUnlessRaises(AssertionError, Profile, 1)
            self.failUnlessRaises(ProfileError, Profile, "Hello")
            p = Profile("1.2.3.4")
            assert p.ip == "1.2.3.4" and type(p.ports_range) is _RangeAny and p.interface == DEFAULT_INTERFACE
            p = Profile("1.2.3.4:*")
            assert p.ip == "1.2.3.4" and type(p.ports_range) is _RangeAny and p.interface == DEFAULT_INTERFACE
            p = Profile("(1.1.1.1)")
            assert p.ip == DEFAULT_IP and type(p.ports_range) is _RangeAny and p.interface == "1.1.1.1"
            p = Profile("23-45")
            assert p.ip == DEFAULT_IP and p.ports_range.start == 23 and p.port_range.end == 45 and \
                p.interface == DEFAULT_INTERFACE

    unittest.main()

