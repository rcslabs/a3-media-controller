/**
 *  NetPoint class
 *
 *
 *
 */
#include "stdafx.h"
#include "conn.h"
#include "stunmessage.h"
#include "ranges.h"

#include "log.h"
#include "sockets.h"


using namespace std;

/*
class NetPointException : public std::exception {
public:
	NetPointException(const char* str) throw() : error_message(str) {}
	virtual ~NetPointException() throw(){}

	virtual const char* what() const throw() {
		return error_message.c_str();
	}

private: 
	std::string error_message;
	NetPointException();
};
*/


//
// Conn class
//

Conn::Conn() : UdpServer(-1) {
	setDataListener(this);
}


bool Conn::open(const string& ports, const string& iface) {
	// find unused port
	RangeParser rangeParser;
	ranges_t rangeResult;
	if(!rangeParser.parse(ports, rangeResult) ) {
		log(LOG_DEBUG, "NetPoint: Could not parse port range " + ports);
		return false;
	}
	Range range(rangeResult);

	Range::iterator begin = range.begin();
	Range::iterator end = range.end();
	Range::iterator start = range.random();
	Range::iterator it = start;
	do {
		{ stringstream s; s << "Trying to open port " << *it; log(LOG_DEBUG, s.str());}
		if(UdpServer::open(*it, iface)) {
			log(LOG_DEBUG, "OPENED SUCCESSFULLY");
			return true;
		}
		if(++it == end)
			it = begin;
	} while(it != start);

	log(LOG_DEBUG, "COULD NOT OPEN ANY PORT!");
	return false;
}




void Conn::onDataReceived(char* buf, size_t len, struct sockaddr *addr, socklen_t addrLen) {
	struct sockaddr_in* client = (struct sockaddr_in*)addr;

	StunMessage stunMessage;
	if(StunMessage::parse(buf, len, &stunMessage)) {
		

		if(stunMessage.isBindingRequest()) {
			string username = stunMessage.getUsername(), localUsername, remoteUsername;
			string::size_type i = username.find(':');
			if(i != string::npos) {
				remoteUsername = username.substr(i+1);
				localUsername = username.substr(0,i);
			}
			log(LOG_DEBUG, "Stun binding request " + localUsername + ":" + remoteUsername);

			points_t points = getPointsByLocalUfrag(localUsername);
			if(points.size()) {
				//
				// Set external remote address to all points, that have the same ice-username and ice-pwd
				//
				for(points_t::const_iterator it = _rtpPoints.begin(); it != _rtpPoints.end(); ++it) {
					(*it)->setExternalRemoteRtpAddress(UdpAddress(addr));
				}

				//
				// ... example point ...
				//
				Point * point = *(points.begin());


				{
					//Binding Success Response
					StunMessage answer(stunMessage);

					//XOR-MAPPED-ADDRESS
					StunAttribute * x = new StunXorMappedAddressAttribute(client->sin_addr, client->sin_port);
					answer.addAttribute(x);
					//stringstream s;
					//s << "Stun attr xor len " << x->getPayloadLength();
					//log(LOG_DEBUG, s.str());

					//MESSAGE-INTEGRITY
					answer.setMessageIntegrityCheck( point->getLocalIcePwd() /*point->getRemoteIcePwd()*/);

					//FINGERPRINT
					answer.setFingerprintCheck();

					char outBuf[1024];
					size_t outLen = 0;
					answer.write(outBuf, outLen);

					// log buffer
					//log(LOG_DEBUG, outBuf, outLen);
					sendData(outBuf, outLen, UdpAddress(addr));
				}
				{
					StunMessage request(E_MESSAGE_BINDING_REQUEST);

					// USERNAME
					request.addAttribute( new StunSimpleAttribute(E_ATTRIBUTE_USERNAME, remoteUsername + ":" + localUsername) );

					// ICE-CONTROLLED
					//char tieBreaker[8] = {0x34, 0xd9, 0xc9, 0xd9, 0xe7, 0xdc, 0x63, 0x4a};
					//answer.attributes[0x802a] = tieBreaker;

					//  PRIORITY
					char priority[4] = {0x6e, 0x00, 0x1e, 0xff};
					request.addAttribute( new StunSimpleAttribute(E_ATTRIBUTE_PRIORITY, priority));

					// USE-CANDIDATE
					request.addAttribute(new StunSimpleAttribute(E_ATTRIBUTE_USE_CANDIDATE, ""));

					// MESSAGE-INTEGRITY
					request.setMessageIntegrityCheck(point->getRemoteIcePwd() /* point->getLocalIcePwd() */);

					//// FINGERPRINT
					request.setFingerprintCheck();

					char outBuf[1024];
					size_t outLen = 0;
					request.write(outBuf, outLen);

					//log(LOG_DEBUG, outBuf, outLen);
					sendData(outBuf, outLen, UdpAddress(addr));
				}

			} else {
				log(LOG_DEBUG, "Binding request for unknown user");
			}
		}
	} else {
		//Point *point = getPointByAddress(client);
		//if(point != NULL) {
		//	point->onConnDataReceived(this, buf, len, addr, addrLen);
		//} else {

		// TODO: JOIN ALL POINTS INTO ONE LIST
        points_t::const_iterator it;
		for(it = _rtpPoints.begin(); it != _rtpPoints.end(); ++it) {
			Point * p = *it;
			if(p->handleConnData(this, buf, len, UdpAddress(addr)))
				return;
		}
		for(it = _rtcpPoints.begin(); it != _rtcpPoints.end(); ++it) {
			Point * p = *it;
			if(p->handleConnData(this, buf, len, UdpAddress(addr)))
				return;
		}

		// LOG
		{
			uint32_t ssrc = ntohl(*(reinterpret_cast<uint32_t *>(buf + 8)));
			stringstream ss;
			ss << "Packet [?ssrc="<<ssrc<<"] from unknown host, I had " << _rtpPoints.size() << " candiate points:";
			log(LOG_DEBUG, ss.str());
			
			for(points_t::const_iterator it = _rtpPoints.begin(); it != _rtpPoints.end(); ++it) {
				Point * p = *it;
				
				if(p->getRemoteRtpConn() == this) {
					stringstream ss;
					ss << "    " << 
					      p->getId() << " --- " << 
					      p->getExternalRemoteRtpAddress().getIpStr() << ":" << 
					      p->getExternalRemoteRtpAddress().getPort() << ", streams: rem=" << p->getRemoteStreams().size();
					log(LOG_DEBUG, ss.str());
					//for(Point::streams_t )
				}

				if(p->getLocalRtpConn() == this) {
					Point::streams_t streams = p->getLocalStreams();

					stringstream ss;
					ss << "    " << p->getId() << " --- " << p->getExternalRemoteRtpAddress().getIpStr() << ":" << p->getExternalRemoteRtpAddress().getPort() << ", streams: loc=" << streams.size();
					log(LOG_DEBUG, ss.str());
					for(Point::streams_t::const_iterator itt = streams.begin();
					                                     itt != streams.end();
					                                     ++itt) {
						Stream * stream = *itt;
						stringstream ss;
						ss << "        stream.ssrc=" << stream->getSsrc();
						log(LOG_DEBUG, ss.str());
					}
				}
			}
		}
	}	
}


/*
void Conn::onMessage(const Message& cmd) {
	if(cmd.getType() == "ADD_POINT") {
		string localIceUfrag    = cmd.getArg("local-ice-ufrag");
		string localIcePwd      = cmd.getArg("local-ice-pwd");
		string remoteIceUfrag   = cmd.getArg("remote-ice-ufrag");
		string remoteIcePwd     = cmd.getArg("remote-ice-pwd");
		string pubSocketAddress = cmd.getArg("pub");
		string subSocketAddress = cmd.getArg("sub");
		string remoteIp         = cmd.getArg("remote-ip");
		string remotePort       = cmd.getArg("remote-port");

		if(localIceUfrag != "" && getPointByUfrag(localIceUfrag) != NULL) {
			log(LOG_DEBUG, "Attempt to add existig point");
			return;
		}

		log(LOG_DEBUG, "Adding point " + localIceUfrag + ":" + remoteIceUfrag + " pub=" + pubSocketAddress + " sub=" + subSocketAddress);

		Point* point = new Point(this, pubSocketAddress, subSocketAddress);
		point->setLocalIceCredentials(localIceUfrag, localIcePwd);
		point->setRemoteIceCredentials(remoteIceUfrag, remoteIcePwd);

		if(remoteIp != "" && remotePort != ""){
			struct sockaddr_in remote;

			remote.sin_family      = AF_INET;
			remote.sin_port        = htons(atoi(remotePort.c_str()));
			remote.sin_addr.s_addr = inet_addr(remoteIp.c_str());
			memset(remote.sin_zero, 0, sizeof remote.sin_zero);

			point->setAddress(remote);


			stringstream l;
			l << "Point has ip and port: " << inet_ntoa(remote.sin_addr) <<":" << ntohs(remote.sin_port);
			log(LOG_DEBUG, l.str());
		}
		point->startThreaded();
		_points.push_back(point);
	}

	if(cmd.getType() == "REMOVE_POINT") {
		// TODO: remove-point
	}
}
*/

void Conn::regRtpListener(Point* point) {
	log(LOG_DEBUG, "Conn::regRtpListener connId=" + getId() + "  pointId=" + point->getId());
	_rtpPoints.push_back(point);
}
void Conn::regRtcpListener(Point* point) {
	log(LOG_DEBUG, "Conn::regRtcpListener connId=" + getId() + "  pointId=" + point->getId());
	_rtcpPoints.push_back(point);
}

void Conn::unregRtpListener(Point* point) {
	_rtpPoints.remove(point);
}
void Conn::unregRtcpListener(Point* point) {
	_rtcpPoints.remove(point);
}


void Conn::stop() {
	_listener = NULL;
	UdpServer::stop();
}

Conn::points_t Conn::getPointsByLocalUfrag(const std::string& ufrag) const {
	points_t result;
	points_t::const_iterator it;

	for(it = _rtpPoints.begin(); it != _rtpPoints.end(); ++it) {
		if((*it)->getLocalIceUfrag() == ufrag)
			result.push_back(*it);
	}

	for(it = _rtcpPoints.begin(); it != _rtcpPoints.end(); ++it) {
		if((*it)->getLocalIceUfrag() == ufrag)
			result.push_back(*it);
	}


	return result;
}


/*Point* Conn::getPointByUfrag(const std::string& ufrag) const {
	Point* point = getRtpPointByUfrag(ufrag);
	if(point) return point;
	return getRtcpPointByUfrag(ufrag);
}


Point* Conn::getRtpPointByUfrag(const std::string& ufrag) const {
	for(points_t::const_iterator it = _rtpPoints.begin(); it != _rtpPoints.end(); ++it) {
		if((*it)->getLocalIceUfrag() == ufrag)
			return *it;
	}
	return NULL;
}


Point* Conn::getRtcpPointByUfrag(const std::string& ufrag) const {
	for(points_t::const_iterator it = _rtcpPoints.begin(); it != _rtcpPoints.end(); ++it) {
		if((*it)->getLocalIceUfrag() == ufrag)
			return *it;
	}
	return NULL;
}
*/

/*Point* Conn::getPointByAddress(struct sockaddr_in* addr) const {
	Point* point = getRtpPointByAddress(addr);
	if(point) return point;
	return getRtcpPointByAddress(addr);
}



Point* Conn::getRtpPointByAddress(struct sockaddr_in* addr) const {
	for(points_t::const_iterator it = _rtpPoints.begin(); it != _rtpPoints.end(); ++it) {
		if((*it)->isExternalRemoteRtpAddress(*addr))
			return *it;
	}
	return NULL;
}
Point* Conn::getRtcpPointByAddress(struct sockaddr_in* addr) const {
	for(points_t::const_iterator it = _rtcpPoints.begin(); it != _rtcpPoints.end(); ++it) {
		//if((*it)->isExternalRemoteRt�pAddress(*addr))
		if((*it)->isExternalRemoteRtpAddress(*addr))
			return *it;
	}
	return NULL;
}
*/

