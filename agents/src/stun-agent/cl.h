#ifndef __CL_H__
#define __CL_H__

#include "stdafx.h"

extern "C" {
#include "srtp.h"
}

#define MAX_KEY_LEN      64


struct Cl {
	//bool parse(int argc, char *argv[]);
	//void help(const std::string& programName) const;

	//std::string in;
	//std::string out;
	std::string key;
	uint32_t    ssrc;

	bool confidentiality;
	bool authentication;

	sec_serv_t getSecServices() const {
		if(confidentiality && authentication)   return sec_serv_conf_and_auth;
		else if(confidentiality)                return sec_serv_conf;
		else if(authentication)                 return sec_serv_auth;
		else                                    return sec_serv_none;
	}
};




#endif
