
#include "stdafx.h"
#include "log.h"
#include "point.h"
#include "conn.h"


using namespace std;

/*Point::Point(UdpServer* out, const std::string& pubSocketAddress, const std::string& subSocketAddress) : _out(out) {
	_pub = new UdpClient(0, pubSocketAddress);
	_sub = new UdpServer(0, subSocketAddress);
	
	_sub->setDataListener(this);
}*/

Point::Point(const string& id): _id(id) {
	_remoteRtpConn   = NULL;
	_remoteRtcpConn  = NULL;
	_localRtpConn    = NULL;
	_localRtcpConn   = NULL;
}

Point::~Point() {
	_remoteRtpConn   = NULL;
	_remoteRtcpConn  = NULL;
	_localRtpConn    = NULL;
	_localRtcpConn   = NULL;

	streams_t::iterator it;

	for(it = _localStreams.begin(); it != _localStreams.end(); ++it) {
		Stream * stream = *it;
		delete stream;
	}

	for(it = _remoteStreams.begin(); it != _remoteStreams.end(); ++it) {
		Stream * stream = *it;
		delete stream;
	}

}


void Point::setIce(const std::string& localIcePair, const std::string& remoteIcePair) {
	int delim = localIcePair.find(':');
	setLocalIceUfrag (localIcePair.substr(0, delim));
	setLocalIcePwd   (localIcePair.substr(delim+1) );

	delim = remoteIcePair.find(':');
	setRemoteIceUfrag(remoteIcePair.substr(0, delim));
	setRemoteIcePwd  (remoteIcePair.substr(delim+1));
}





bool Point::handleConnData(Conn* conn, char* buffer, size_t len, const UdpAddress& fromAddr) {
	Stream * stream = NULL;

	/*
	log(LOG_DEBUG, "Point::handleConnData conn=" + conn->getId());
	log(LOG_DEBUG, "    My _remoteRtpConn is " + _remoteRtpConn->getId());
	log(LOG_DEBUG, "    My _remoteRtcpConn is " + _remoteRtcpConn->getId());
	log(LOG_DEBUG, "    My _localRtpConn is " + _localRtpConn->getId());
	log(LOG_DEBUG, "    My _localRtpConn is " + _localRtcpConn->getId());
    */

	if(conn == _remoteRtpConn) {
		if(!isExternalRemoteRtpAddress(fromAddr))
			return false;

		uint32_t ssrc  = ntohl(*(reinterpret_cast<uint32_t *>(buffer + 8)));
		stream = findRemoteStreamBySsrc(ssrc);
		if(stream) {
			stream->onRtpDataReceived(buffer, len, fromAddr);
			return true;
		}
	}

	if(conn == _remoteRtcpConn) {
		if(!isExternalRemoteRtcpAddress(fromAddr))
			return false;

		uint32_t ssrc  = ntohl(*(reinterpret_cast<uint32_t *>(buffer + 4)));    // SSRC of packet sender
		stream = findRemoteStreamBySsrc(ssrc);
		if(stream) {
			stream->onRtcpDataReceived(buffer, len, fromAddr);
			return true;
		}
	}

	if(conn == _localRtpConn) {
		uint32_t ssrc = ntohl(*(reinterpret_cast<uint32_t *>(buffer + 8)));

		for(streams_t::iterator it = _localStreams.begin(); it != _localStreams.end(); ++it) {
			Stream* stream  = *it;
			if(stream->getSsrc() == ssrc || 
			   stream->getSsrc() == 0) {           // accepts any

				stringstream ss;
				ss << "Point: I've received RTP (internal) and I can work with it!!! p.ssrc=" << ssrc << " my.ssrc=" << stream->getSsrc();
				log(LOG_DEBUG, ss.str());

				stream->onRtpDataReceived(buffer, len, fromAddr);
				return true;
			}
		}
	}

	if(conn == _localRtcpConn) {
		uint32_t ssrc = ntohl(*(reinterpret_cast<uint32_t *>(buffer + 4)));

		for(streams_t::iterator it = _localStreams.begin(); it != _localStreams.end(); ++it) {
			Stream* stream  = *it;
			if(stream->getSsrc() == ssrc ||
			   stream->getSsrc() == 0) {

				stringstream ss;
				ss << "Point: I've received RTCP (internal) and I can work with it!!! p.ssrc=" << ssrc << " my.ssrc=" << stream->getSsrc();
				log(LOG_DEBUG, ss.str());
				stream->onRtcpDataReceived(buffer, len, fromAddr);
				return true;
			}
		}
	}

	return false;
}


void Point::startThreaded() {
	//_sub->startThreaded();
}
