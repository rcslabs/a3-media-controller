//
//
//
//
//

#include "stdafx.h"
#include "cli.h"
#include "log.h"
#include "point.h"
#include "conn.h"
#include "conn-collection.h"
#include "stream.h"


using namespace std;


//
// MessageDispatcher class
//
class MessageDispatcher : public IMessageListener, public IMessageSender {
public:
	MessageDispatcher(IMessageSender* sender);

	void onMessage(const Message&);

	void sendMessage(const Message&) const;

private:
	typedef std::map<std::string, Point*> points_t;

	points_t            _points;
	ConnCollection      _connections;
	IMessageSender*     _sender;

	bool removePoint(const string& pointId);


	void bindRemoteRtp(Point*, Conn*);
	void bindRemoteRtcp(Point*, Conn*);
	void bindLocalRtp(Point*, Conn*);
	void bindLocalRtcp(Point*, Conn*);

	void unbindRemoteRtp(Point*);
	void unbindRemoteRtcp(Point*);
	void unbindLocalRtp(Point*);
	void unbindLocalRtcp(Point*);
};



//
// MessageDispather implementation
//
MessageDispatcher::MessageDispatcher(IMessageSender* sender) : _sender(sender)
{}

void MessageDispatcher::onMessage(const Message& msg) {
	if(msg.getType() == "OPEN_CONN") {
		std::string iface = msg.getArg("iface", "0.0.0.0");
		std::string ports = msg.getArg("port", "0");

		Conn* conn = _connections.createConn(ports, iface);
		if(conn) {
			Message answer = msg.reply("OPEN_CONN_OK");
			answer.setArg("port",  conn->getPortStr());
			answer.setArg("iface", conn->getIface());
			answer.setArg("id",    conn->getId());
			sendMessage(answer);
		} else {
			Message answer = msg.reply("OPEN_CONN_FAILED");
			sendMessage(answer);
		}

	} else if(msg.getType() == "CLOSE_CONN") {
		std::string id = msg.getArg("id");
		Conn* conn = _connections.getConnById(id);
		if(conn) {
			Conn::points_t points = conn->getRtpPoints();
			Conn::points_t::const_iterator it;
			for(it = points.begin(); it != points.end(); ++it) {
				Point* point = *it;
				if(point->getLocalRtpConn() == conn)  unbindLocalRtp(point);
				if(point->getRemoteRtpConn() == conn) unbindRemoteRtp(point);
			}
			points = conn->getRtcpPoints();
			for(it = points.begin(); it != points.end(); ++it) {
				Point* point = *it;
				if(point->getLocalRtcpConn() == conn)  unbindLocalRtcp(point);
				if(point->getRemoteRtcpConn() == conn) unbindRemoteRtcp(point);
			}
		}

		if(_connections.closeConn(id)) {
			Message answer = msg.reply("CLOSE_CONN_OK");
			sendMessage(answer);
		} else {
			Message answer = msg.reply("CLOSE_CONN_FAILED");
			sendMessage(answer);
		}

	} else if(msg.getType() == "ADD_POINT") {
		std::string id          = msg.getArg("id");
		Conn*       localRtp    = _connections.getConnById(msg.getArg("localRtp"));
		Conn*       localRtcp   = _connections.getConnById(msg.getArg("localRtcp"));
		Conn*       remoteRtp   = _connections.getConnById(msg.getArg("remoteRtp"));
		Conn*       remoteRtcp  = _connections.getConnById(msg.getArg("remoteRtcp"));
		std::string localIce    = msg.getArg("localIce");
		std::string remoteIce   = msg.getArg("remoteIce");

		UdpAddress externalRemoteRtp  = UdpAddress::parse(msg.getArg("externalRemoteRtp"));
		UdpAddress externalRemoteRtcp = UdpAddress::parse(msg.getArg("externalRemoteRtcp"));

		stringstream ss;
		ss << "Extenal Remote RTP Addr " << externalRemoteRtp.getIpStr() << " : " << externalRemoteRtp.getPort();
		log(LOG_DEBUG, ss.str());


		if(id.length() && localRtp /*&& localRtcp */ && remoteRtp /*&& remoteRtcp*/ ) {
			Point* point = new Point(id);
			_points.insert(std::make_pair(id, point));

			if(localIce.length() && remoteIce.length())
				point->setIce(localIce, remoteIce);

			point->setExternalRemoteRtpAddress(externalRemoteRtp);
			// TODO: set RTCP ADDRR
			//point->setExternalRemoteRtcpAddress(externalRemoteRtp);

			bindRemoteRtp (point, remoteRtp);
			bindRemoteRtcp(point, remoteRtcp);
			bindLocalRtp  (point, localRtp);
			bindLocalRtcp (point, localRtcp);

			Message answer = msg.reply("ADD_POINT_OK");
			sendMessage(answer);
		} else {
			Message answer = msg.reply("ADD_POINT_FAILED");
			sendMessage(answer);
		}


	} else if(msg.getType() == "REMOVE_POINT") {
		std::string id  = msg.getArg("id");

		points_t::iterator it = _points.find(id);
		if(it != _points.end()) {
			Point * point = it->second;
			unbindRemoteRtp(point);
			unbindRemoteRtcp(point);
			unbindLocalRtp(point);
			unbindLocalRtcp(point);
		}

		if(removePoint(id)) {
			sendMessage(msg.reply("REMOVE_POINT_OK"));
		} else {
			sendMessage(msg.reply("REMOVE_POINT_FAILED"));
		}


	} else if(msg.getType() == "ADD_REMOTE_STREAM") {

		std::string pointId = msg.getArg("pointId");

		UdpAddress rtpAddress  = UdpAddress::parse(msg.getArg("rtp"));
		UdpAddress rtcpAddress = UdpAddress::parse(msg.getArg("rtcp"));

		points_t::iterator it = _points.find(pointId);
		if(it != _points.end() && rtpAddress.isSet() /*&& rtcpAddress.isSet() */) {
			Point * point = it->second;
			Stream * stream = new Stream();
			std::string ssrc = msg.getArg("ssrc");
			std::string key  = msg.getArg("key");
			std::string newSsrc = msg.getArg("newSsrc");

			stream->setDestinationAddress(rtpAddress, rtcpAddress);

			if(ssrc.length())
				stream->setSsrc(strtoul(ssrc.c_str(), NULL, 10));

			if(newSsrc.length())
				stream->setNewSsrc(strtoul(newSsrc.c_str(), NULL, 10));

			if(key.length()) {
				stream->setKey(key);
				stream->setMode(Stream::MODE_DECRYPT);
			}

			point->addRemoteStream(stream);

			Message answer = msg.reply("ADD_REMOTE_STREAM_OK");
			sendMessage(answer);
		} else {
			Message answer = msg.reply("ADD_REMOTE_STREAM_FAILED");
			sendMessage(answer);
		}

	} else if(msg.getType() == "REMOVE_LOCAL_STREAM") {
		std::string pointId = msg.getArg("pointId");
		std::string strSsrc = msg.getArg("ssrc");
		uint32_t ssrc = strtoul(strSsrc.c_str(), NULL, 10);

		points_t::iterator it = _points.find(pointId);
		if(it != _points.end() && ((it->second))->removeLocalStream(ssrc)) {
			Message answer = msg.reply("REMOVE_LOCAL_STREAM_OK");
			sendMessage(answer);
		} else {
			Message answer = msg.reply("REMOVE_LOCAL_STREAM_FAILED");
			sendMessage(answer);
		}

	} else if(msg.getType() == "ADD_LOCAL_STREAM") {
		std::string pointId = msg.getArg("pointId");
		points_t::iterator it = _points.find(pointId);
		if(it != _points.end()) {
			Point * point = it->second;
			Stream * stream = new Stream();
			std::string ssrc = msg.getArg("ssrc");
			std::string key  = msg.getArg("key");

			if(ssrc.length())
				stream->setSsrc(strtoul(ssrc.c_str(), NULL, 10));

			if(key.length()) {
				stream->setKey(key);
				stream->setMode(Stream::MODE_ENCRYPT);
			}

			point->addLocalStream(stream);

			Message answer = msg.reply("ADD_LOCAL_STREAM_OK");
			sendMessage(answer);
		} else {
			Message answer = msg.reply("ADD_LOCAL_STREAM_FAILED");
			sendMessage(answer);
		}


	} else if(msg.getType() == "DIE" || msg.getType() == "q") {
		exit(0);

	} else {
		// unknown message
		log(LOG_DEBUG, "Unknown message type:" + msg.getType());
	}
}


void MessageDispatcher::bindRemoteRtp(Point* point, Conn* conn) {
	unbindRemoteRtp(point);
	point->setRemoteRtpConn(conn);
	conn->regRtpListener(point);
}
void MessageDispatcher::bindRemoteRtcp(Point* point, Conn* conn) {
	unbindRemoteRtcp(point);
	point->setRemoteRtcpConn(conn);
	conn->regRtcpListener(point);
}
void MessageDispatcher::bindLocalRtp(Point* point, Conn* conn) {
    log(LOG_DEBUG, "bindLocalRtp");
	unbindLocalRtp(point);
	point->setLocalRtpConn(conn);
	conn->regRtpListener(point);
}
void MessageDispatcher::bindLocalRtcp(Point* point, Conn* conn) {
    log(LOG_DEBUG, "bindLocalRtcp");
	unbindLocalRtcp(point);
	point->setLocalRtcpConn(conn);
	conn->regRtcpListener(point);
}
void MessageDispatcher::unbindRemoteRtp(Point* point) {
	Conn* conn = point->getRemoteRtpConn();
	if(conn) conn->unregRtpListener(point);
	point->setRemoteRtpConn(NULL);
}
void MessageDispatcher::unbindRemoteRtcp(Point* point) {
	Conn* conn = point->getRemoteRtcpConn();
	if(conn) conn->unregRtcpListener(point);
	point->setRemoteRtcpConn(NULL);
}
void MessageDispatcher::unbindLocalRtp(Point* point) {
	Conn* conn = point->getLocalRtpConn();
	if(conn) conn->unregRtpListener(point);
	point->setLocalRtpConn(NULL);
}
void MessageDispatcher::unbindLocalRtcp(Point* point) {
	Conn* conn = point->getLocalRtcpConn();
	if(conn) conn->unregRtcpListener(point);
	point->setLocalRtcpConn(NULL);
}




void MessageDispatcher::sendMessage(const Message& msg) const {
	if(_sender != NULL)
		_sender->sendMessage(msg);
}


bool MessageDispatcher::removePoint(const string& pointId) {
	points_t::iterator it = _points.find(pointId);

	if(it == _points.end()) {
		return false;
	}
	Point* point = it->second;
	_points.erase(it);
	delete point;
	return true;
}




int main(int argc, char *argv[]) {
	srand((unsigned int)time(NULL));
	//logger_setup("stun",  LOG_ALL);
	logger_setup("stun",  LOG_NONE);

#ifdef _WIN32
	WSAData wsa;
	WSAStartup(MAKEWORD(1, 1), &wsa);
#endif


	// initialize srtp library 
	err_status_t  status = srtp_init();
	if (status) {
		log(LOG_ERROR, "srtp initialization failed with error code " + status);
		exit(1);
	}


	try {
		Cli cli;
		MessageDispatcher messageDispatcher(&cli);
 
 		cli.setMessageListener(&messageDispatcher);

		cli.start();

	} catch(std::exception& e) {
		log(LOG_DEBUG, string("error=") + e.what());
	}

	return 0;
}


