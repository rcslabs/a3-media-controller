#ifndef __CONN_COLLECTION_H__
#define __CONN_COLLECTION_H__


#include "stdafx.h"
#include "conn.h"


class ConnCollection {
public:
	Conn* createConn(const std::string& ports = "0", const std::string& iface="0.0.0.0");
	Conn* getConnById(const std::string& id) const;
	bool closeConn(const std::string& id);

private:
	typedef std::map<std::string, Conn*> connections_t;
	connections_t _connections;
};

#endif // __CONN_COLLECTION_H__
