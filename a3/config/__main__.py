#! /usr/bin/env python
"""
a3.config demo
execute:
    # python -m a3.config
"""

__author__ = 'RCSLabs'


from ..logging import LOG
from ..config import CommandLineConfig, IniConfig, DefaultConfig

config = CommandLineConfig(IniConfig(DefaultConfig()))
LOG.info("Config:\n%s", config)
