#ifndef __LOG_H__
#define __LOG_H__


#include <string>
const unsigned int LOG_DEBUG = 1 << 0;
const unsigned int LOG_INFO  = 1 << 1;
const unsigned int LOG_ERROR = 1 << 2;
const unsigned int LOG_NET   = 1 << 3;

const unsigned int LOG_NONE = 0;
const unsigned int LOG_ALL = 0xFFFFFFFF;

void logger_setup(const std::string& p_loggerName, unsigned int p_logLevel = LOG_ALL);

void log(unsigned int level, const std::string&);
void log(unsigned int level, const char*);
void log(unsigned int level, const char* buffer, size_t len);


#endif
