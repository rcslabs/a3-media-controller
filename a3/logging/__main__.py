#! /usr/bin/env python
"""
a3.logging demo
execute:
    # python -m a3.logging
"""


__author__ = 'RCSLabs'

from ..logging import LOG

LOG.info("Info message")
LOG.debug("Debug message")
LOG.warning("Warning message")
LOG.error("Error message")

try:
    raise Exception("Exception message")
except Exception as e:
    LOG.exception(e)
