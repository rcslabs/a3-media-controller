#include "log.h"
#include <stdio.h>
#include <sstream>


using namespace std;

std::string   loggerName;
unsigned int  logLevel;

void logger_setup(const std::string& p_loggerName, unsigned int p_logLevel) {
	loggerName = p_loggerName;
	logLevel   = p_logLevel;
}


void log(unsigned int level, const std::string& msg) {
	log(level, msg.c_str());
}


void log(unsigned int level, const char* msg) {
	if(level & logLevel){
		fprintf(stderr, "[%s] %s\n", loggerName.c_str(), msg);
		fflush(stderr);
	}
}

void log(unsigned int level, const char* buffer, size_t len) {
	stringstream s;
	s << "(" << len << ") ";
	s.setf(ios_base::hex, ios::basefield);
	for(size_t i = 0; i < len; i++) {
		if( i % 16 == 0) s << endl;
		char nbuf[200];
		sprintf(nbuf, "%02x ", (unsigned char)buffer[i]);
		s << nbuf;
	}
	log(level, s.str());
}