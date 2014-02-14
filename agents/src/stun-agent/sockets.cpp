#include "sockets.h"
#include "log.h"
#include "stdafx.h"

using namespace std;







UdpAddress UdpAddress::parse(const string& str) {
	struct sockaddr_in addr;

	string::size_type pos1 = str.find("://");
	if(pos1 == string::npos)
		return UdpAddress();
	pos1 += 3;

	string::size_type pos2 = str.find(":", pos1);
	if(pos2 == string::npos)
		return UdpAddress();
	pos2 += 1;

	string host = str.substr(pos1, pos2-pos1-1);
	string port = str.substr(pos2);

	memset(&addr, 0, sizeof(struct sockaddr_in));
	addr.sin_family      = AF_INET;
	addr.sin_port        = htons(atoi(port.c_str()));
	addr.sin_addr.s_addr = inet_addr(host.c_str());

	return UdpAddress(reinterpret_cast<struct sockaddr*>(&addr));
}


//
// DataReceiver
//
pthread_t DataReceiver::startThreaded() {
	pthread_t pointThread;
#ifdef _WIN32
	DWORD threadId;
	pointThread = CreateThread( NULL, 0, threadFunc, this, 0, &threadId);
#else
	pthread_create(&pointThread, NULL, threadFunc, this);
#endif
	return pointThread;
}

void DataReceiver::setDataListener(IDataListener* listener) {
	_listener = listener;
}

THREAD_FUNC DataReceiver::threadFunc(void *vptr_args) {
	DataReceiver* dataReceiver = (DataReceiver*)vptr_args;
	dataReceiver->start();
	return NULL;
}

void DataReceiver::notify(char* buffer, size_t len, struct sockaddr *addr, socklen_t addrLen) {
	if(_listener != NULL)
		_listener->onDataReceived(buffer, len, addr, addrLen);
}

////////////////////////////////////////////////////////////////////////////////



UdpServer::UdpServer(int port, const string& iface) : _socket(0), _port(-1), _iface(""){
	if(port != -1) {
		open(port, iface);
		// todo: check result;
	}
}
UdpServer::~UdpServer() {
	stop();
}


bool UdpServer::open(int port, const string& iface) {
	struct sockaddr_in server;

	if ((_socket = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
		log(LOG_DEBUG, "UdpServer::open : Failed to open");
		return false;
	}

	server.sin_family      = AF_INET;
	server.sin_port        = htons(port);
	server.sin_addr.s_addr = inet_addr(iface.c_str());

	if(bind(_socket, (struct sockaddr *)&server, sizeof(server)) < 0) {
		log(LOG_DEBUG, "UdpServer::open : Failed to bind");
		return false;
	}

	struct sockaddr_in result;
	socklen_t namelen = sizeof(result);
	if (getsockname(_socket, (struct sockaddr *) &result, &namelen) < 0) {
		log(LOG_DEBUG, "UdpServer::open : Failed to getsockname");
	}

	_port = ntohs(result.sin_port);
	_iface = inet_ntoa(result.sin_addr);
	return true;
}



void UdpServer::start() {
	log(LOG_DEBUG, "Listening...");
	struct sockaddr_in client;
	socklen_t client_address_size = sizeof(client);

	char print_buf[165536];

	char buf[65536];

	int received = 0; 

	while(1) {
		received = recvfrom(_socket, buf, sizeof(buf), 0, (struct sockaddr *) &client, &client_address_size);
		if(received >= 0) {
			sprintf(print_buf, "UdpServer::received [%d]  from %s:%d on %s:%d",
			   received,
			   inet_ntoa(client.sin_addr),
			   ntohs(client.sin_port),
			   _iface.c_str(), _port
			   );
			log(LOG_NET, print_buf);

			notify(buf, received, (struct sockaddr *) &client, client_address_size);

		} else {
			log(LOG_DEBUG, "received 0 bytes on socket");
			break;
		}
	}
}
void UdpServer::stop() {
	if(_socket) {
		stringstream ss;
		ss << "UdpServer::close socket " << _iface << ":" << _port;
		log(LOG_NET, ss.str());

		shutdown(_socket, 2);
		#ifdef _WIN32
		closesocket(_socket);
		#else 
		close(_socket);
		#endif
		_socket = 0;
	}
}

void UdpServer::sendData(char* buffer, size_t len, const UdpAddress& to) {
	struct sockaddr toAddr;
	socklen_t toAddrLen;
	if(to.getSockaddr(&toAddr, toAddrLen)) {
		stringstream ss;
		ss << "UdpServer::sendData [" << len << "] from " << _iface << ":" << _port<< " to " << to.getIpStr() << ":" << to.getPort();
		log(LOG_NET, ss.str());

		ssize_t outLen = sendto(_socket, buffer, len, 0, &toAddr, toAddrLen);

		if(outLen == -1) {                       // error
			perror("sendto :");
		}
	} else {
		stringstream ss;
		ss << "UdpServer::sendData [" << len << "] -- destination failed";
		log(LOG_NET, ss.str());
	}
}

