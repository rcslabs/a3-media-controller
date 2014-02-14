#!/usr/bin/env python


class SemanticError(Exception):
    def __init__(self, value):
        assert isinstance(value, str)
        self.value = value

    def __str__(self):
        return str(self.value)


if __name__ == "__main__":
    import unittest

    def raises_semantic_error(param):
        raise SemanticError("TEST ERROR: " + param)

    class SdpSemanticErrorTest(unittest.TestCase):
        def testRaise(self):
            try:
                raises_semantic_error("x")
            except SemanticError as e:
                self.failUnless(str(e) == "TEST ERROR: x")
            else:
                self.fail('Did not see SdpSemanticError')

    unittest.main()
