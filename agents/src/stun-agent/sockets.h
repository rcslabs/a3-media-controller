#ifndef __SOCKETS_H__
#define __SOCKETS_H__

#include "stdafx.h"


#include <stdlib.h>
#include <string>


class Address {
public:
	Address() {
		_isSet = false;
	}

	virtual bool getSockaddr(struct sockaddr *, socklen_t&) const = 0;

	bool isSet() const {
		return _isSet;
	};

protected:
	bool _isSet;
};



class UdpAddress : public Address {
public:
	UdpAddress() {};
	UdpAddress(struct sockaddr * addr) {
		_isSet = true;
		_addr = *(struct sockaddr_in*)addr;
	}

	bool getSockaddr(struct sockaddr *addr, socklen_t& len) const {
		if(!_isSet)
			return false;
		len = sizeof(struct sockaddr_in);
		memcpy(addr, &_addr, len);
		return true;
	}

	std::string getIpStr() const {
		return inet_ntoa(getIp());
	}
	in_addr getIp() const {
		if(!isSet())
			return in_addr();
		return _addr.sin_addr;
	}
	u_short getPort() const {
		if(!isSet())
			return 0;
		return ntohs(_addr.sin_port);
	}

	bool operator==(const UdpAddress& right) const {
		if(!isSet() && !right.isSet()) return true;
		return isSet() == right.isSet() && getIp().s_addr == right.getIp().s_addr && getPort() == right.getPort();
	}


	static UdpAddress parse(const std::string& str);

private:
	struct sockaddr_in _addr;
};



 

class IDataListener {
public:
	virtual void onDataReceived(char* buffer, size_t len, struct sockaddr *, socklen_t) = 0;
};

/*

class IDataSender {
public:
	virtual void sendData(char* buffer, size_t len) = 0;
};
*/



class DataReceiver {
public:
	virtual void start() = 0;
	virtual void stop() = 0;

	pthread_t startThreaded();

	void setDataListener(IDataListener*);


protected:
	IDataListener* _listener;

	static THREAD_FUNC threadFunc(void *vptr_args);
	
	void notify(char* buffer, size_t len, struct sockaddr *, socklen_t);
};










class UdpServer : public DataReceiver {
public:
	UdpServer(int port, const std::string& iface = "0.0.0.0");
	virtual ~UdpServer();

	void start();
	void stop();

	//
	// return opened udp port and interface
	//
	int         getPort()  const { return _port;  }
	std::string getIface() const { return _iface; }


	void sendData(char* buffer, size_t len, const UdpAddress& to);

protected:
	bool open(int port, const std::string& iface = "0.0.0.0");

private:
	UdpServer();

	int             _socket;
	int             _port;
	std::string     _iface;
};


#endif

