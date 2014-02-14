#include "log.h"
#include "cli.h"
#include <iostream>
#include <string>
#include <stdio.h>

using namespace std;


////////////////////////////////////////////////////////////////////////////////
//
//  Message
//
Message::Message(const std::string& type, const arguments_t& arguments) : _type(type), _arguments(arguments)
{}

std::string Message::getType() const {
	return _type;
}

void Message::setType(const std::string& type) {
	_type = type;
}

std::string Message::getArg(const std::string& name, const std::string& defaultValue) const {
	arguments_t::const_iterator it = _arguments.find(name);
	if(it == _arguments.end())
		return defaultValue;
	else
		return it->second;
}

bool Message::hasArg(const std::string& name) const {
	return _arguments.find(name) != _arguments.end();
}

void Message::setArg(const std::string& name, const std::string& value) {
	if(name == "type")
		setType(value);
	else
		_arguments[name] = value;
}

Message::arguments_t Message::getArgs() const {
	return _arguments;
}

void Message::setArgs(const arguments_t& arguments) {
	for(arguments_t::const_iterator it = arguments.begin(); it != arguments.end(); ++it)
		setArg(it->first, it->second);
}

Message Message::reply(const std::string& type, const arguments_t& arguments) const {
	Message result(_type, _arguments);
	if(type.length() > 0)
		result.setType(type);
	result.setArgs(arguments);
	return result;
}


std::string Message::toString() const {
	//std::string result = getType();
	std::string result = "type=" + getType();
	for(arguments_t::const_iterator it = _arguments.begin(); it != _arguments.end(); ++it) {
		result += " " + it->first + "=" + it->second;
	}
	return result;
}





////////////////////////////////////////////////////////////////////////////////
//
// Cli: command line interface
//
Cli::Cli() : _listener(NULL)
{}

void Cli::sendMessage(const Message& msg) const {
	log(LOG_DEBUG, "Sending " + msg.toString());
	printf("%s\n", msg.toString().c_str());
	fflush(stdout);
}

void Cli::setMessageListener(IMessageListener* listener) {
	_listener = listener;
}


void Cli::parse(const std::string& line) {
		int state = 0;
		std::string name = "", value = "";
		Message msg;

		for(size_t i = 0; i < line.length(); i++) {
			char c = line[i];
			
			switch(state) {
				case 0 :
					if(c == '=') {
							value = "";
							state = 1;
					} else if(c == ' ') {
							if(msg.getArgs().size() == 0)
								msg.setType(name);
							name = "";
					}else {
							name += c;
					}
					break;
            
				case 1:
					if(c == ' ') {
							msg.setArg(name, value);
							//log(LOG_DEBUG, name + "=" + value);
							name="";
							value = "";
							state = 0;
					} else {
							value += c;
					}
					break;
			}
		}
		if(name.length()) {
			if(value.length()) {
				msg.setArg(name, value);
			} else {
				if(msg.getArgs().size() == 0)
					msg.setType(name);
			}
		}

		log(LOG_DEBUG, "Received: " + msg.toString());

		if(_listener && msg.getType().length() != 0) {
			_listener->onMessage(msg);
		}	
}


void Cli::start() {
	std::string line;

	while(1) {
		std::getline(std::cin, line);
		if(std::cin.eof())
			break;

		log(LOG_DEBUG, "received: " + line);
		parse(line);
	}
}




bool parseAddress(const std::string& str, struct sockaddr_in& addr) {
	string::size_type pos1 = str.find("://") + 3;
	if(pos1 == string::npos)
		return false;
	string::size_type pos2 = str.find(":", pos1) + 1;
	if(pos2 == string::npos)
		return false;
	string host = str.substr(pos1, pos2-pos1-1);
	string port = str.substr(pos2);

	//log(LOG_DEBUG, "parseAddress");
	//log(LOG_DEBUG,host);
	//log(LOG_DEBUG,port);

	memset(&addr, 0, sizeof(struct sockaddr_in));
	addr.sin_family      = AF_INET;
	addr.sin_port        = htons(atoi(port.c_str()));
	addr.sin_addr.s_addr = inet_addr(host.c_str());

	return true;
}
