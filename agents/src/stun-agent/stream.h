#ifndef __STREAM_H__
#define __STREAM_H__

#include "stdafx.h"
#include "log.h"
#include "codec.h"

class Conn;

class Stream {
public:

	static const int MODE_NONE = 0;
	static const int MODE_ENCRYPT = 1;
	static const int MODE_DECRYPT = 2;

	Stream();
	~Stream();

	bool onRtpDataReceived (char* buffer, size_t len, const UdpAddress& fromAddr);
	bool onRtcpDataReceived(char* buffer, size_t len, const UdpAddress& fromAddr);

	void setMode(int mode);

	unsigned long getSsrc() const {
		return _ssrc;
	}
	void setSsrc(unsigned long ssrc) {
		_ssrc = ssrc;
	}
	void setNewSsrc(unsigned long ssrc) {
		_newSsrc = ssrc;
	}

	void setKey(const std::string& key) {
		_key = key;
	}

	void setDestinationAddress(const UdpAddress& rtpAddress, const UdpAddress& rtcpAddress);

	void setDestinationRtpConn(Conn* rtpConn)   { _rtpDestinationConn = rtpConn;   }
	void setDestinationRtcpConn(Conn* rtcpConn) { _rtcpDestinationConn = rtcpConn; }

private:
	unsigned long   _ssrc;
	unsigned long   _newSsrc;
	std::string     _key;
	int             _mode;

	UdpAddress      _rtpDestinationAddress;
	UdpAddress      _rtcpDestinationAddress;

	Conn*           _rtpDestinationConn;
	Conn*           _rtcpDestinationConn;

	Codec *         _codec;
};


#endif // __STREAM_H__
