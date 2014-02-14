
#include "stdafx.h"
#include "codec.h"
#include "log.h"

using namespace std;

Codec::Codec(const Cl& cl) {
	//_in  = new UdpServer(0,cl.in);
	//_out = new UdpClient(0,cl.out);
	//_in->setDataListener(this);

	initPolicy(cl);
	initReceiver(cl);
}

Codec::~Codec() {
	log(LOG_DEBUG, "SRTP_DEALLOC");
	srtp_dealloc(_srtp_ctx);
}



void Codec::initPolicy(const Cl& cl) {
	// set up the srtp policy and master key
	sec_serv_t sec_servs = cl.getSecServices();

	if (sec_servs) {
		/* 
		 * create policy structure, using the default mechanisms but 
		 * with only the security services requested on the command line,
		 * using the right SSRC value
		 */
		switch (sec_servs) {
			case sec_serv_conf_and_auth:
				//log(LOG_DEBUG, "crypto_policy_set_rtp_default\n");
				crypto_policy_set_rtp_default(&_policy.rtp);
				crypto_policy_set_rtcp_default(&_policy.rtcp);
				break;
			case sec_serv_conf:
				//log(LOG_DEBUG, "crypto_policy_set_aes_cm_128_null_auth");
				crypto_policy_set_aes_cm_128_null_auth(&_policy.rtp);
				crypto_policy_set_rtcp_default(&_policy.rtcp);      
				break;
			case sec_serv_auth:
				//log(LOG_DEBUG, "crypto_policy_set_null_cipher_hmac_sha1_80");
				crypto_policy_set_null_cipher_hmac_sha1_80(&_policy.rtp);
				crypto_policy_set_rtcp_default(&_policy.rtcp);
				break;
			case sec_serv_none:
				break;
		} 

		char* key = new char[MAX_KEY_LEN];
		int len = hex_string_to_octet_string(key, const_cast<char*>(cl.key.c_str()), MASTER_KEY_LEN*2);

		/* check that hex string is the right length */
		if (len < MASTER_KEY_LEN*2) {
			fprintf(stderr, 
			        "error: too few digits in key/salt "
			        "(should be %d hexadecimal digits, found %d)\n",
			        MASTER_KEY_LEN*2, len);
			exit(1);    
		}
		if (cl.key.length() > MASTER_KEY_LEN*2) {
			fprintf(stderr, 
			        "error: too many digits in key/salt "
			        "(should be %d hexadecimal digits, found %u)\n",
			        MASTER_KEY_LEN*2, (unsigned)cl.key.length());
			exit(1);    
		}

		_policy.ssrc.type       = ssrc_specific;
		_policy.ssrc.value      = cl.ssrc;
		_policy.key             = (uint8_t *) key;
		//_policy.ekt             = NULL;
		_policy.next            = NULL;
		//_policy.window_size     = 128;
		//_policy.allow_repeat_tx = 0;

		//_policy.rtp.sec_serv = sec_servs;
		//_policy.rtcp.sec_serv = sec_serv_none;  /* we don't do RTCP anyway */

	} else {
		/*
		 * we're not providing security services, so set the policy to the
		 * null policy
		 *
		 * Note that this policy does not conform to the SRTP
		 * specification, since RTCP authentication is required.  However,
		 * the effect of this policy is to turn off SRTP, so that this
		 * application is now a vanilla-flavored RTP application.
		 */
		_policy.key                 = NULL;
		_policy.ssrc.type           = ssrc_specific;
		_policy.ssrc.value          = cl.ssrc;
		_policy.rtp.cipher_type     = NULL_CIPHER;
		_policy.rtp.cipher_key_len  = 0; 
		_policy.rtp.auth_type       = NULL_AUTH;
		_policy.rtp.auth_key_len    = 0;
		_policy.rtp.auth_tag_len    = 0;
		_policy.rtp.sec_serv        = sec_serv_none;   
		_policy.rtcp.cipher_type    = NULL_CIPHER;
		_policy.rtcp.cipher_key_len = 0; 
		_policy.rtcp.auth_type      = NULL_AUTH;
		_policy.rtcp.auth_key_len   = 0;
		_policy.rtcp.auth_tag_len   = 0;
		_policy.rtcp.sec_serv       = sec_serv_none;   
		_policy.next                = NULL;
	}
}

void Codec::initReceiver(const Cl& cl) {

	err_status_t status = srtp_create(&_srtp_ctx, &_policy);

	if (status) {
		stringstream s;
		s << "error: srtp_create() failed with code " << status;
		log(LOG_ERROR, s.str());
		exit(1);
	}
}

