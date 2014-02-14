#!/usr/bin/env python
"""
base Gst


"""

__author__ = 'RCSLabs'


import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject, GLib, Gio
GObject.threads_init()
Gst.init(None)

#
#import gio
# When using gi.repository you must not import static modules like "gobject". Please change all occurrences of
# "import gobject" to "from gi.repository import GObject
#


class IGstElementContainer(object):
    pass
