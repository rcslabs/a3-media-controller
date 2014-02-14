#ifndef __STUNMESSAGE_h__
#define __STUNMESSAGE_h__


#include "rfc5389.h"



class StunAttribute {
public:
	StunAttribute(StunAttributeType type = E_ATTRIBUTE_UNKNOWN) : _type(type) {}

	virtual ~StunAttribute() {}

	StunAttributeType getType() const {
		return _type;
	}


	void write(char* buffer, size_t& ptr);


	//
	//
	//
	virtual int getPayloadLength()  = 0;

	//
	//
	//
	virtual void writePayload(char* buffer) = 0;


private:
	StunAttributeType _type;
};



//
//
//
class StunSimpleAttribute : public StunAttribute {
public:
	StunSimpleAttribute(StunAttributeType type = E_ATTRIBUTE_UNKNOWN,
	                    std::string payload = "")
	                   : StunAttribute(type), _payload(payload) {}

	int getPayloadLength() {
		return _payload.length();
	}

	void writePayload(char* buffer) {
		memcpy(buffer, _payload.c_str(), getPayloadLength());
	}

	std::string getPayload() const { return _payload; }

private:
	std::string _payload;
};



//
//
//
class StunXorMappedAddressAttribute : public StunAttribute {
public:
	StunXorMappedAddressAttribute(struct in_addr host, unsigned short port)
	                             : StunAttribute(E_ATTRIBUTE_XOR_MAPPED_ADDRESS) {
		_ma.reserved = 0;
		_ma.protocol_family = 1;    // IPv4
		_ma.ip   = host.s_addr ^ htonl(0x2112a442);
		_ma.port = port ^ htons(0x2112);
	}

	int getPayloadLength() {
		return sizeof(stun_xor_mapped_address_t);
	}

	void writePayload(char* buffer) {
		memcpy(buffer, (void*)&_ma, getPayloadLength());
	}

private:
	stun_xor_mapped_address_t _ma;
	StunXorMappedAddressAttribute();
};




//
//
//
class StunMessage {
public:
	StunMessage(StunMessageType type = E_MESSAGE_UNKNOWN);
	StunMessage(const StunMessage&);
	~StunMessage();


	StunAttribute* getAttribute(StunAttributeType attributeType) const;

	void write(char* buffer, size_t& ptr);

	std::string getUsername() const;

	StunMessageType getType() const { return _type; }
	bool isBindingRequest() const { return getType() == E_MESSAGE_BINDING_REQUEST; }

	void setTransactionId(const unsigned char* tid) {
		memcpy(_transactionId, tid, TRANSACTION_ID_LENGTH);
	}
	void addAttribute(StunAttribute* attribute) {
		_attributes.push_back(attribute);
	}
	void addAttribute(StunAttributeType type, std::string value) {
		addAttribute(new StunSimpleAttribute(type, value));
	}
	
	void setMessageIntegrityCheck(std::string integrityPwd) { _checkMessageIntegrity = true; _integrityPwd = integrityPwd; }
	void cancelMessageIntegrityCheck() { _checkMessageIntegrity = false; }
	void setFingerprintCheck() { _checkFingerprint = true; }

	static bool parse(char* msg, int len, StunMessage* out);

private:
	typedef std::vector<StunAttribute*> attributes_t;

	StunMessageType _type;
	unsigned char   _transactionId[TRANSACTION_ID_LENGTH];
	attributes_t    _attributes;
	bool            _checkMessageIntegrity;
	std::string     _integrityPwd;
	bool            _checkFingerprint;
	
	
	StunMessage& operator=(const StunMessage&);

	void clear();
};



#endif

