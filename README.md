alena
PATH=./agents:$PATH GST_DEBUG=3,python:5,gnl*:5 ./media_controller.py --host=85.195.85.107



yana:
PATH=./agents:$PATH GST_DEBUG=3,python:5,gnl*:5 ./media_controller.py --host=85.195.85.109







easy_install:

sudo apt-get install python-setuptools




sudo easy_install typecheck
sudo easy_install redis

python-gobject




Ubuntu (gstreamer 1.0):


sudo apt-add-repository ppa:gstreamer-developers/ppa
sudo apt-get update

-- Installing GStreamer 1.0 packages


sudo apt-get install python-gi python3-gi \
    gstreamer1.0-tools \
    gir1.2-gstreamer-1.0 \
    gir1.2-gst-plugins-base-1.0 \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-libav





Install gstreamer plugins
    yum search gstreamer | grep gstreamer
    yum install gstreamer1-plugins-base.x86_64
    yum install gstreamer1-plugins-good.x86_64
    yum install gstreamer-plugins-bad-free.x86_64 




Install libav
    yum install gstreamer1-devel gstreamer1-plugins-base-devel orc-devel bzip2-devel yasm
    wget http://hany.sk/mirror/rpmfusion/free/fedora/releases/18/Everything/source/SRPMS/gstreamer1-libav-1.0.2-2.fc18.src.rpm
    rpmbuild --rebuild ./gstreamer1-libav-1.0.2-2.fc18.src.rpm
    
Ugly

    wget http://download1.rpmfusion.org/free/fedora/releases/18/Everything/source/SRPMS/gstreamer1-plugins-ugly-1.0.2-2.fc18.src.rpm
    rpmbuild --rebuild ./gstreamer1-plugins-ugly-1.0.2-2.fc18.src.rpm
    rpm -i /root/rpmbuild/RPMS/x86_64/gstreamer1-plugins-ugly-1.0.2-2.fc18.x86_64.rpm
    
    
    



Used RFC

SDP:
    RFC 3264 - An Offer/Answer Model with the Session Description Protocol (SDP)
    RFC 3388 - Grouping of Media Lines in the Session Description Protocol (SDP)
    RFC 3605 - Real Time Control Protocol (RTCP) attribute in Session Description Protocol (SDP)
    RFC 4566 - SDP: Session Description Protocol
    RFC 4568 - Session Description Protocol (SDP) Security Descriptions for Media Streams
    RFC 4574 - The Session Description Protocol (SDP) Label Attribute
    RFC 5124 - Extended Secure RTP Profile for Real-time Transport Control Protocol (RTCP)-Based Feedback (RTP/SAVPF)
    RFC 5245 - Interactive Connectivity Establishment (ICE): A Protocol for Network Address Translator (NAT) Traversal for Offer/Answer Protocols
    RFC 5576 - Source-Specific Media Attributes in the Session Description Protocol (SDP)
    RFC 5761 - Multiplexing RTP Data and Control Packets on a Single Port
    RFC 5888 - The Session Description Protocol (SDP) Grouping Framework
    RFC 6236 - Negotiation of Generic Image Attributes in the Session Description Protocol (SDP)

    Draft - Multiplexing Negotiation Using Session Description Protocol (SDP) Port Numbers
    Draft - Media level ice-options SDP attribute

http://tools.ietf.org/html/rfc6455              The WebSocket Protocol



TO IMPLEMENT:
    RFC 4572 - Connection-Oriented Media Transport over the Transport Layer Security (TLS) Protocol in the Session Description Protocol (SDP)
