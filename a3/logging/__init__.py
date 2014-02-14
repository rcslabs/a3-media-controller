#!/usr/bin/env python
"""
logging
export LOG object
"""

__author__ = 'RCSLabs'


import logging

_FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=_FORMAT, level=logging.DEBUG)

LOG = logging.getLogger("MC")


