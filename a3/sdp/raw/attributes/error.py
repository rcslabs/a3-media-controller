#!/usr/bin/env python


class ParseError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


if __name__ == "__main__":
    import unittest

    def raises_parse_error(param):
        raise ParseError("TEST ERROR: " + param)

    class SdpParseErrorTest(unittest.TestCase):
        def testRaise(self):
            try:
                raises_parse_error("x")
            except ParseError as e:
                self.failUnless(str(e) == "TEST ERROR: x")
            else:
                self.fail('Did not see SdpParseError')

    unittest.main()
