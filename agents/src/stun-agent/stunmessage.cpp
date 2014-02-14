
#include "stunmessage.h"
#include "log.h"

#ifdef _WIN32
extern "C" {
#endif
	#include "gnulib/hmac.h"
#ifdef _WIN32
}
#endif


#include "stdafx.h"

using namespace std;

void StunAttribute::write(char* buffer, size_t& ptr) {
	// write header
	stun_attribute_header_t* attr = (stun_attribute_header_t*)(&buffer[ptr]);
	attr->type   = htons(_type);
	attr->length = htons(this->getPayloadLength());
	ptr += sizeof(stun_attribute_header_t);

	// write body
	this->writePayload(buffer + ptr);
	ptr += this->getPayloadLength();

	// write padding
	while(ptr % 4 != 0) {
		buffer[ptr] = 0;
		ptr++;
	}
}



//
// StunMessage
//
StunMessage::StunMessage(StunMessageType type) : _type(type){
	for(int i = 0; i < 12; i++)
		_transactionId[i] = (char)(rand() % 256);
	_checkMessageIntegrity = false;
	_checkFingerprint = false;
}
StunMessage::StunMessage(const StunMessage& r) {
	setTransactionId(r._transactionId);
	_checkMessageIntegrity = r._checkMessageIntegrity;
	_checkFingerprint = r._checkFingerprint;
	switch(r._type) {
		case E_MESSAGE_BINDING_REQUEST:
			_type = E_MESSAGE_BINDING_SUCCESSFULL_RESPONSE;
			break;
		default:
			_type = E_MESSAGE_UNKNOWN;
			break;
	}
}
StunMessage::~StunMessage() {
	clear();
}

void StunMessage::clear() {
	for(attributes_t::iterator it = _attributes.begin(); it != _attributes.end(); ++it)
		delete *it;
	_attributes.clear();
}





StunAttribute* StunMessage::getAttribute(StunAttributeType attributeType) const {
	for(attributes_t::const_iterator it = _attributes.begin();
	    it != _attributes.end();
	    ++it) {
			if((*it)->getType() == attributeType)
				return (*it);
	}
	return NULL;
}

std::string StunMessage::getUsername() const {
	StunAttribute* attr = getAttribute(E_ATTRIBUTE_USERNAME);
	StunSimpleAttribute* usernameAttr = attr ? dynamic_cast<StunSimpleAttribute*>(attr) : NULL;
	return usernameAttr ? usernameAttr->getPayload() : NULL;
}





bool StunMessage::parse(char* msg, int len, StunMessage* out) {
	if(len < HEADER_LENGTH) {
		//log(LOG_DEBUG, "len < HEADER_LENGTH");
		return false;
	}

	if((msg[0] & 0xC0) != 0) {             //header.first two bits == 0 0;
		//stringstream s;
		//s<<"msg[0] && 0xC0 != 0 ;       msg[0]=" << (unsigned int)(msg[0]);
		//log(LOG_DEBUG, s.str());
		return false;
	}

	stun_message_header_t* header = (stun_message_header_t*)msg;

	if(len != HEADER_LENGTH + ntohs(header->body_length)) {          // header has
		//log(LOG_DEBUG, "len != HEADER_LENGTH + ntohs(header->body_length)");
		return false;
	}
	
	//log(LOG_DEBUG, "Check magic");

	if(ntohl(header->magic_cookie) != 0x2112a442)
		return false;

	//log(LOG_DEBUG, "Seems to be stun message");

	out->_type = static_cast<StunMessageType>( ntohs(header->type) );
	out->setTransactionId(header->transaction_id);
	out->clear();

	int p = HEADER_LENGTH;  // starting after header there are attributes
	char buf[1024];
	while(p < len) {
		if(p + ATTR_MIN_LENGTH > len) {
			//log(LOG_DEBUG, "p + ATTR_MIN_LENGTH > len");
			return false;         // no bytes for attribute
		}
		
		stun_attribute_header_t* attr = reinterpret_cast<stun_attribute_header_t*>(msg + p);

		StunAttributeType attr_type = static_cast<StunAttributeType>(ntohs(attr->type));
		int attr_data_len = ntohs(attr->length);

		if(p + ATTR_MIN_LENGTH + attr_data_len > len) {
			return false;
		}
		
		//
		//
		//
		sprintf(buf, "Got attr %d [%d]", attr_type,attr_data_len );
		std::string attr_data(msg + p + ATTR_MIN_LENGTH, attr_data_len);

		out->addAttribute(attr_type, attr_data);

		p = p + ATTR_MIN_LENGTH + attr_data_len;
		while(p%4 != 0) p++;
	}

	return true;
}



uint32_t Crc32(unsigned char *buf, size_t len) {
	uint32_t crc_table[256];
	uint32_t crc; int i, j;
 
	for (i = 0; i < 256; i++) {
		crc = i;
		for (j = 0; j < 8; j++)
			crc = crc & 1 ? (crc >> 1) ^ 0xEDB88320UL : crc >> 1;
 
		crc_table[i] = crc;
	};
 
	crc = 0xFFFFFFFFUL;
 
	while (len--) 
		crc = crc_table[(crc ^ *buf++) & 0xFF] ^ (crc >> 8);
 
	return crc ^ 0xFFFFFFFFUL;
}



void StunMessage::write(char* buffer, size_t& len) {
	
	// fill header
	len = HEADER_LENGTH;
	stun_message_header_t* header = reinterpret_cast<stun_message_header_t*>(buffer);
	header->type = htons(getType());
	
	//std::stringstream s;
	//s << "Writing message type=" <<  int(getType());
	//log(LOG_DEBUG, s.str());


	header->magic_cookie= htonl(0x2112a442);
	memcpy(header->transaction_id, _transactionId, TRANSACTION_ID_LENGTH);

	for(attributes_t::const_iterator it = _attributes.begin(); it != _attributes.end(); ++it) {
		StunAttribute *a = *it;
		a->write(buffer, len);
	}

	if(_checkMessageIntegrity) {
		header->body_length = htons(len - HEADER_LENGTH + 24);                  // set length as if attribute has been added, and its len is 24 = 4(header) + 20(sha1)
		char hmac[65536];
		const char *key = _integrityPwd.c_str();
		int keylen = _integrityPwd.length();

		hmac_sha1(key, keylen, buffer, len, hmac);

		StunSimpleAttribute a(E_ATTRIBUTE_MESSAGE_INTEGRITY, std::string(hmac, 20));
		a.write(buffer, len);
	}

	if(_checkFingerprint) {
		header->body_length = htons(len - HEADER_LENGTH + 8);                  // set length as if attribute has been added, and its len is 8 = 4(header) + 4(crc32)
		uint32_t crc32 = Crc32((unsigned char*)buffer, len);
		crc32 ^= 0x5354554e;
		crc32 = htonl(crc32);
		StunSimpleAttribute a(E_ATTRIBUTE_FINGERPRINT, std::string(reinterpret_cast<char*>(&crc32), 4));
		a.write(buffer, len);
	}

	header->body_length = htons(len - HEADER_LENGTH);
}

