#ifndef __POINT_H__
#define __POINT_H__


#include "stdafx.h"
#include "sockets.h"
#include "stream.h"

class Conn;

class Point{
public:
	typedef std::vector<Stream*> streams_t;

	Point(const std::string & id);
	~Point();

	void startThreaded();

	std::string getId() const { return _id; }

	std::string getLocalIceUfrag()  const { return _localIceUfrag;  }
	std::string getLocalIcePwd()    const { return _localIcePwd;    }
	std::string getRemoteIceUfrag() const { return _remoteIceUfrag; }
	std::string getRemoteIcePwd()   const { return _remoteIcePwd;   }

	void setLocalIceUfrag (const std::string& value) { _localIceUfrag  = value; }
	void setLocalIcePwd   (const std::string& value) { _localIcePwd    = value; }
	void setRemoteIceUfrag(const std::string& value) { _remoteIceUfrag = value; }
	void setRemoteIcePwd  (const std::string& value) { _remoteIcePwd   = value; }

	void setIce(const std::string& localIcePair, const std::string& remoteIcePair);



	void setExternalRemoteRtpAddress(const UdpAddress & addr) {
		_remoteExternalRtpAddress = addr;
		//
		// TODO: rebase local streams
		//
		for(streams_t::iterator it = _localStreams.begin(); it != _localStreams.end(); ++it) {
			(*it)->setDestinationAddress(addr, addr);
		}
	}

	UdpAddress getExternalRemoteRtpAddress() const {
		return _remoteExternalRtpAddress;
	}


	streams_t getRemoteStreams() const { return _remoteStreams; }
	streams_t getLocalStreams() const { return _localStreams; }


	//
	// TODO: 
	//
	//bool isExternalRemoteRtpAddress(const struct sockaddr_in& addr) const {
	//	return (_remoteExternalRtpAddress.sin_addr.s_addr == addr.sin_addr.s_addr) &&
	//	       (_remoteExternalRtpAddress.sin_port == addr.sin_port);
	//}
	bool isExternalRemoteRtpAddress(const UdpAddress& rtpAddress) const {
		return _remoteExternalRtpAddress == rtpAddress;
	}
	bool isExternalRemoteRtcpAddress(const UdpAddress& rtcpAddres) const {
		// TODO: FIX!!!
		return isExternalRemoteRtpAddress(rtcpAddres);
	}


	bool handleConnData(Conn*, char* buffer, size_t len, const UdpAddress& fromAddr);

	//bool onUnknownConnDataReceived(Conn* ,char* buffer, size_t len, struct sockaddr *, socklen_t);


	void addRemoteStream(Stream* stream) {
		_remoteStreams.push_back(stream);   // remote stream (from client to room) sends data using local stream
		stream->setDestinationRtpConn(_localRtpConn);
		stream->setDestinationRtcpConn(_localRtcpConn);				
	}

	void addLocalStream(Stream* stream) {
		_localStreams.push_back(stream);    // local stream (from room to client) sends data using remote stream
		stream->setDestinationRtpConn(_remoteRtpConn);
		stream->setDestinationRtcpConn(_remoteRtcpConn);
		stream->setDestinationAddress(_remoteExternalRtpAddress, _remoteExternalRtpAddress);
	}


	bool removeLocalStream(uint32_t ssrc) {
		for(streams_t::iterator it = _localStreams.begin(); it != _localStreams.end(); ++it) {
			Stream * stream = *it;
			if(stream->getSsrc() == ssrc) {
				_localStreams.erase(it);
				delete stream;
				return true;
			}
		}
		return false;
	}


	Conn* getRemoteRtpConn()  const { return _remoteRtpConn;  }
	Conn* getRemoteRtcpConn() const { return _remoteRtcpConn; }
	Conn* getLocalRtpConn()  const  { return _localRtpConn;   }
	Conn* getLocalRtcpConn() const  { return _localRtcpConn;  }

	void setRemoteRtpConn(Conn* rtpConn)   { 
		_remoteRtpConn  = rtpConn;  
		for(streams_t::const_iterator it = _remoteStreams.begin(); it != _remoteStreams.end(); ++it)
			(*it)->setDestinationRtpConn(rtpConn);
	}
	void setRemoteRtcpConn(Conn* rtcpConn) { 
		_remoteRtcpConn = rtcpConn; 
		for(streams_t::const_iterator it = _remoteStreams.begin(); it != _remoteStreams.end(); ++it)
			(*it)->setDestinationRtcpConn(rtcpConn);
	}
	void setLocalRtpConn(Conn* rtpConn)    {
		_localRtpConn   = rtpConn;  
		for(streams_t::const_iterator it = _localStreams.begin(); it != _localStreams.end(); ++it)
			(*it)->setDestinationRtpConn(rtpConn);
	}
	void setLocalRtcpConn(Conn* rtcpConn)  { 
		_localRtcpConn  = rtcpConn; 
		for(streams_t::const_iterator it = _localStreams.begin(); it != _localStreams.end(); ++it)
			(*it)->setDestinationRtcpConn(rtcpConn);
	}



private:

	streams_t _localStreams;
	streams_t _remoteStreams;

	Conn* _remoteRtpConn;
	Conn* _remoteRtcpConn;
	Conn* _localRtpConn;
	Conn* _localRtcpConn;


	std::string	        _id;

	std::string         _localIceUfrag;
	std::string         _localIcePwd;
	std::string         _remoteIceUfrag;
	std::string         _remoteIcePwd;

	UdpAddress          _remoteExternalRtpAddress;


	Stream* findRemoteStreamBySsrc(unsigned long ssrc) const {
		for(streams_t::const_iterator it = _remoteStreams.begin(); it != _remoteStreams.end(); ++it)
			if((*it)->getSsrc() == 0 ||                                        // accepts any ssrc
			   (*it)->getSsrc() == ssrc)
				return (*it);
		return NULL;
	}



	Point();
};



#endif

