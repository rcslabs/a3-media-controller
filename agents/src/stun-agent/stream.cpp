#include "stdafx.h"
#include "stream.h"
#include "codec.h"
#include "cl.h"
#include "conn.h"

using namespace std;
/*
OPEN_CONN port=50000
OPEN_CONN port=50001
ADD_POINT id=xxx localRtp=udp://0.0.0.0:50000/ localRtcp=udp://0.0.0.0:50000/ remoteRtp=udp://0.0.0.0:50001/ remoteRtcp=udp://0.0.0.0:50001/
ADD_REMOTE_STREAM key=325b26a87034dffd4dd5a2af2a78391fc5233eadb3e65cae7ba215b8da8f pointId=xxx rtcp=udp://192.168.1.38:50001 rtp=udp://192.168.1.38:50000 ssrc=2371502630




*/





string srtp_error_message(err_status_t err) {
	switch(err) {
		case err_status_ok:
			return "nothing to report";
		case err_status_fail:
			return "unspecified failure";
		case err_status_bad_param:
			return "unsupported parameter";
		case err_status_alloc_fail:
			return "couldn't allocate memory";
		case err_status_dealloc_fail:
			return "couldn't deallocate properly";
		case err_status_init_fail:
			return "couldn't initialize";
		case err_status_terminus:
			return "can't process as much data as requested";
		case err_status_auth_fail:
			return "authentication failure";
		case err_status_cipher_fail:
			return "cipher failure";
		case err_status_replay_fail:
			return "replay check failed (bad index)";
		case err_status_replay_old:
			return "replay check failed (index too old)";
		case err_status_algo_fail:
			return "algorithm failed test routine";
		case err_status_no_such_op:
			return "unsupported operation";
		case err_status_no_ctx:
			return "no appropriate context found";
		case err_status_cant_check:
			return "unable to perform desired validation";
		case err_status_key_expired:
			return "can't use key any more";
		default:
			return "unknown";
	}
}


Stream::Stream() :  _ssrc(0),  _newSsrc(0), _key(""), _mode(0)
{
	_codec = NULL;
	_rtpDestinationConn = NULL;
	_rtcpDestinationConn = NULL;
}

Stream::~Stream() {
	log(LOG_DEBUG, "Removing stream");

	_rtpDestinationConn = NULL;
	_rtcpDestinationConn = NULL;
	if(_codec) {
		delete _codec;
		_codec = NULL;
	}
}


//void Stream::setDestinationConn(Conn* rtpConn, Conn* rtcpConn) {
//	_rtpDestinationConn = rtpConn;
//	_rtcpDestinationConn = rtpConn;
//}

void Stream::setDestinationAddress(const UdpAddress& rtpAddress, const UdpAddress& rtcpAddress) {
	_rtpDestinationAddress = rtpAddress;
	_rtcpDestinationAddress = rtcpAddress;
}


void Stream::setMode(int mode) {
	_mode = mode;
	if(mode == MODE_ENCRYPT || mode == MODE_DECRYPT) {
		// init encryption/decryption context
		Cl cl;
		cl.authentication = true;
		cl.confidentiality = true;
		cl.key = _key;
		cl.ssrc = _ssrc;
		_codec = new Codec(cl);
	}
}

bool Stream::onRtpDataReceived( char* buffer, size_t len, const UdpAddress& fromAddr) {
	if(_mode == MODE_DECRYPT || _mode == MODE_ENCRYPT)  {
		uint32_t ssrc = ntohl(*(reinterpret_cast<uint32_t *>(buffer + 8)));
		stringstream ss; ss << "Got data[" << len << "] ssrc=" << ssrc << "   self.ssrc=" << _ssrc;
		log(LOG_DEBUG, ss.str());

		err_status_t error = (_mode == MODE_DECRYPT) ? 
		                            srtp_unprotect(_codec->_srtp_ctx, buffer, reinterpret_cast<int*>(&len)) : 
		                            srtp_protect(_codec->_srtp_ctx, buffer, reinterpret_cast<int*>(&len));

		if(error) {
			stringstream s; s << "Error rtp: srtp failed with code " << error << " (" << srtp_error_message(error) <<")"; log(LOG_DEBUG, s.str());
			return false;
		}
		log(LOG_DEBUG, (_mode == MODE_DECRYPT) ? "Decrypted ok" : "Encrypted ok");
	}

	if(_rtpDestinationConn) {
		if(_newSsrc) {
			*(reinterpret_cast<uint32_t *>(buffer + 8)) = htonl(_newSsrc);
		}

		_rtpDestinationConn->sendData(buffer, len, _rtpDestinationAddress);
	} else
		log(LOG_DEBUG, "Stream: Do not know where to send");

	return true;
}

bool Stream::onRtcpDataReceived( char* buffer, size_t len, const UdpAddress& fromAddr) {
	if(_mode == MODE_DECRYPT || _mode == MODE_ENCRYPT)  {

		uint32_t ssrc = ntohl(*(reinterpret_cast<uint32_t *>(buffer + 4)));
		stringstream ss; ss << "Got RTCP[" << len << "] ssrc=" << ssrc << "   self.ssrc=" << _ssrc;
		log(LOG_DEBUG, ss.str());

		err_status_t error = (_mode == MODE_DECRYPT) ? 
		                            srtp_unprotect_rtcp(_codec->_srtp_ctx, buffer, reinterpret_cast<int*>(&len)) : 
		                            srtp_protect_rtcp(_codec->_srtp_ctx, buffer, reinterpret_cast<int*>(&len));

		if(error) {
			stringstream s; s << "Error: srtp (RTCP) failed with code " << error << " (" << srtp_error_message(error) <<")"; log(LOG_DEBUG, s.str());
			return false;
		}
		log(LOG_DEBUG, (_mode == MODE_DECRYPT) ? "Decrypted RTCP ok" : "Encrypted RTCP  ok");
	}

	if(_rtcpDestinationConn)
		_rtcpDestinationConn->sendData(buffer, len, _rtcpDestinationAddress);
	else
		log(LOG_DEBUG, "Stream: Do not know where to send");

	return true;
}

