#!/usr/bin/env python
"""
Command line config
"""

__author__ = 'RCSLabs'


from ._base import ChainedConfig, ConfigParseError
from ..logging import LOG
import sys
import re


class CommandLineConfig(ChainedConfig):
    def __init__(self, next_):
        super(CommandLineConfig, self).__init__(next_)
        for opt in sys.argv[1:]:
            try:
                self.parse_from_line(opt)
            except ConfigParseError:
                LOG.error("Config: Error parsing command line argument: %s", opt)

    @classmethod
    def get_value(cls, param_name):
        for opt in sys.argv[1:]:
            g = re.match(cls.LINE_PARSER, opt)
            if g is not None and g.group(1) == param_name:
                return g.group(2)
        return None

