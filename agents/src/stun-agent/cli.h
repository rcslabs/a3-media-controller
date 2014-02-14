#ifndef __CLI_H__
#define __CLI_H__


#include "stdafx.h"


// forward declaration
class Message;



//
// interface IMessageListener
//
class IMessageListener {
public:
	virtual void onMessage(const Message&) = 0;
};



//
// interface IMessageSender
//
class IMessageSender {
public:
	virtual void sendMessage(const Message&) const = 0;
};





//
// class Message
//
class Message {
public:
	typedef std::map<std::string, std::string> arguments_t;

	Message(const std::string& type = "", const arguments_t& arguments = arguments_t());


	std::string getType() const;

	void setType(const std::string&);


	bool hasArg(const std::string& name) const;

	std::string getArg(const std::string& name, const std::string& defaultValue = "") const;

	void setArg(const std::string& name, const std::string& value);


	arguments_t getArgs() const;

	void setArgs(const arguments_t& arguments);
	

	Message reply(const std::string& type = "", const arguments_t& arguments = arguments_t()) const;


	std::string toString() const;

private:
	std::string  _type;
	arguments_t  _arguments;
};










//
// class Cli - command line interface
//
class Cli : public IMessageSender {
public:
	Cli();
	
	//
	//
	//
	void setMessageListener(IMessageListener*);
	
	//
	//
	//
	void start();

	//
	//
	//
	void sendMessage(const Message&) const;

private:
	IMessageListener * _listener;

	void parse(const std::string& line);
};


// udp://127.0.0.1:10567
bool parseAddress(const std::string& str, struct sockaddr_in& addr);



#endif
