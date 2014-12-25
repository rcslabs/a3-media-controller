#!/usr/bin/env python
"""
 Run tests for sdp serialize/deserialize
 # python -m a3.session_description.marshal.sdp
"""

from ._deserialize import deserialize_sdp
from ._serialize import serialize_sdp


s_sdp = """v=0
o=1015 1887833595819407616 3449214676547904840 IN IP4 192.168.1.252
s=-
c=IN IP4 192.168.1.252
t=0 0
m=audio 5006 RTP/AVP 8
a=rtpmap:8 PCMA/8000
a=zrtp-hash:1.10 e3f44e20e5cf6e3e70e375bfb11bd4919469afc3d4784047939100c5bf0ef4d6
"""


session_description = deserialize_sdp(s_sdp)
sdp = serialize_sdp(session_description)
print sdp
