#!/usr/bin/env python
"""
Config uses ini file
"""

__author__ = 'RCSLabs'

from ._base import ChainedConfig, ConfigParseError
from .command_line_config import CommandLineConfig
from ..logging import LOG
import os


CONFIG_FILE_NAME = "config.ini"


class IniConfig(ChainedConfig):
    def __init__(self, next_, files=None):
        """
        extract config file name from command line or config.ini from current dir or from home dir and read it
        """
        ChainedConfig.__init__(self, next_)
        self.params = {}

        if files is None:
            file_from_cl = CommandLineConfig.get_value("config")
            if file_from_cl:
                files = (file_from_cl,)
            else:
                files = (CONFIG_FILE_NAME, "~/" + CONFIG_FILE_NAME)

        for f in files:
            if f is not None:
                if os.path.isfile(f):
                    self.read_ini_file(f)
                    break

    def read_ini_file(self, file_name):
        with open(file_name) as f:
            file_name = os.path.abspath(f.name)
            LOG.info("Config: Reading ini file: %s", file_name)
            for (line_number, line) in enumerate(f.readlines()):
                line = line.rstrip()
                if len(line) and line[0] != "#":
                    try:
                        self.parse_from_line(line)
                    except ConfigParseError:
                        LOG.error("Config: File %s, line %d: Error reading value `%s`", file_name, line_number, line)
