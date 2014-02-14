#ifndef __CONN_H__
#define __CONN_H__

#include "cli.h"
#include "point.h"
#include "sockets.h"



class Conn : public UdpServer, public IDataListener {
public:
	typedef std::list<Point*> points_t;


	Conn();
	~Conn() {}

	bool open(const std::string& ports = "0", const std::string& iface = "0.0.0.0");
	
	//
	//  from IMessageListener
	//
	//void onMessage(const Message&);


	void regRtpListener(Point*);
	void regRtcpListener(Point*);
	void unregRtpListener(Point*);
	void unregRtcpListener(Point*);


	//
	// from IDataListener
	//
	void onDataReceived(char* buf, size_t len, struct sockaddr *addr, socklen_t addrLen);


	std::string getPortStr()const {
		char port_str[12];
		sprintf(port_str, "%d", getPort());
		return port_str;
	}
	std::string getId() const {
		return  "udp://" + getIface() + ":" + getPortStr() + "/";
	}

	//
	//
	//
	points_t getPointsByLocalUfrag(const std::string& ufrag) const;

	//Point* getPointByUfrag(const std::string& ufrag) const;
	//Point* getPointByAddress(struct sockaddr_in*) const;

	points_t getRtpPoints() const { return _rtpPoints; }
	points_t getRtcpPoints() const { return _rtcpPoints; }

	void stop();


private:
	points_t _rtpPoints;
	points_t _rtcpPoints;
};


#endif // __CONN_H__
