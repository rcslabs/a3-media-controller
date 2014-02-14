#ifndef __CODEC_H__
#define __CODEC_H__


#include "stdafx.h"
#include "cl.h"
#include "sockets.h"

#define MASTER_KEY_LEN   30

extern "C" {
	//#include <datatypes.h>
	//#include <rtp.h>
	//#include <srtp.h>
}




class Codec  {
public:
	Codec(const Cl& cl);
	~Codec();

	//void onDataReceived(char* buffer, size_t len, struct sockaddr *, socklen_t);

	//void start() {
	//	_in->start();
	//}
	//void startThreaded() {
	//	_in->startThreaded();
	//}


	DataReceiver *    _in;
//	IDataSender *     _out;
	srtp_policy_t     _policy;
	srtp_ctx_t *      _srtp_ctx;

	void initPolicy(const Cl& cl);
	void initReceiver(const Cl& cl);

private:
	Codec();
};







#endif
