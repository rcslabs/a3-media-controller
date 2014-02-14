
#include "stdafx.h"
#include "conn-collection.h"

using namespace std;

Conn* ConnCollection::createConn(const std::string &ports, const std::string& iface) {
	Conn *conn = new Conn();
	if(conn->open(ports, iface)) {
		_connections.insert(make_pair(conn->getId(), conn));
		conn->startThreaded();
		return conn;
	} else {
		delete conn;
		return NULL;
	}
}

Conn* ConnCollection::getConnById(const std::string& id) const {
	connections_t::const_iterator it = _connections.find(id);
	return it != _connections.end() ? it->second : NULL;
}

bool ConnCollection::closeConn(const std::string& id) {
	connections_t::iterator it = _connections.find(id);
	if(it == _connections.end()) {
		return false;
	}

	Conn* conn = it->second;
	_connections.erase(it);
	
	//delete conn;
	//
	conn->stop();

	return true;
}
