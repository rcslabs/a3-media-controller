#ifndef __RFC5389_H__
#define __RFC5389_H__



#include "stdafx.h"


//  ice-char      = ALPHA / DIGIT / "+" / "/"
//  ice-pwd-att   = "ice-pwd" ":" password
//  ice-ufrag-att = "ice-ufrag" ":" ufrag
//  password      = 22*256ice-char
//  ufrag         = 4*256ice-char


#ifdef _WIN32
#define PACKED
#pragma pack (push)
#pragma pack (1)
#else
#define PACKED   __attribute__((packed))
#endif

typedef enum pj_stun_msg_type
{
	PJ_STUN_BINDING_REQUEST	               = 0x0001,
	PJ_STUN_BINDING_RESPONSE               = 0x0101,
	PJ_STUN_BINDING_ERROR_RESPONSE         = 0x0111,
	PJ_STUN_BINDING_INDICATION             = 0x0011,
	PJ_STUN_SHARED_SECRET_REQUEST          = 0x0002,
	PJ_STUN_SHARED_SECRET_RESPONSE         = 0x0102,
	PJ_STUN_SHARED_SECRET_ERROR_RESPONSE   = 0x0112,
	PJ_STUN_ALLOCATE_REQUEST               = 0x0003,
	PJ_STUN_ALLOCATE_RESPONSE              = 0x0103,
	PJ_STUN_ALLOCATE_ERROR_RESPONSE        = 0x0113,
	PJ_STUN_REFRESH_REQUEST                = 0x0004,
	PJ_STUN_REFRESH_RESPONSE               = 0x0104,
	PJ_STUN_REFRESH_ERROR_RESPONSE         = 0x0114,
	PJ_STUN_SEND_INDICATION                = 0x0016,
	PJ_STUN_DATA_INDICATION                = 0x0017,
	PJ_STUN_CREATE_PERM_REQUEST            = 0x0008,
	PJ_STUN_CREATE_PERM_RESPONSE           = 0x0108,
	PJ_STUN_CREATE_PERM_ERROR_RESPONSE     = 0x0118,
	PJ_STUN_CHANNEL_BIND_REQUEST           = 0x0009,
	PJ_STUN_CHANNEL_BIND_RESPONSE          = 0x0109,
	PJ_STUN_CHANNEL_BIND_ERROR_RESPONSE    = 0x0119
} pj_stun_msg_type;




typedef enum pj_stun_attr_type
{
    PJ_STUN_ATTR_MAPPED_ADDR               = 0x0001,/**< MAPPED-ADDRESS.  */
    PJ_STUN_ATTR_RESPONSE_ADDR             = 0x0002,/**< RESPONSE-ADDRESS (deprcatd)*/
    PJ_STUN_ATTR_CHANGE_REQUEST            = 0x0003,/**< CHANGE-REQUEST (deprecated)*/
    PJ_STUN_ATTR_SOURCE_ADDR               = 0x0004,/**< SOURCE-ADDRESS (deprecated)*/
    PJ_STUN_ATTR_CHANGED_ADDR              = 0x0005,/**< CHANGED-ADDRESS (deprecatd)*/
    PJ_STUN_ATTR_USERNAME                  = 0x0006,/**< USERNAME attribute.	    */
    PJ_STUN_ATTR_PASSWORD                  = 0x0007,/**< was PASSWORD attribute.   */
    PJ_STUN_ATTR_MESSAGE_INTEGRITY         = 0x0008,/**< MESSAGE-INTEGRITY.	    */
    PJ_STUN_ATTR_ERROR_CODE                = 0x0009,/**< ERROR-CODE.		    */
    PJ_STUN_ATTR_UNKNOWN_ATTRIBUTES        = 0x000A,/**< UNKNOWN-ATTRIBUTES.	    */
    PJ_STUN_ATTR_REFLECTED_FROM            = 0x000B,/**< REFLECTED-FROM (deprecatd)*/
    PJ_STUN_ATTR_CHANNEL_NUMBER            = 0x000C,/**< TURN CHANNEL-NUMBER	    */
    PJ_STUN_ATTR_LIFETIME                  = 0x000D,/**< TURN LIFETIME attr.	    */
    PJ_STUN_ATTR_MAGIC_COOKIE              = 0x000F,/**< MAGIC-COOKIE attr (deprec)*/
    PJ_STUN_ATTR_BANDWIDTH                 = 0x0010,/**< TURN BANDWIDTH (deprec)   */
    PJ_STUN_ATTR_XOR_PEER_ADDR             = 0x0012,/**< TURN XOR-PEER-ADDRESS	    */
    PJ_STUN_ATTR_DATA                      = 0x0013,/**< DATA attribute.	    */
    PJ_STUN_ATTR_REALM                     = 0x0014,/**< REALM attribute.	    */
    PJ_STUN_ATTR_NONCE                     = 0x0015,/**< NONCE attribute.	    */
    PJ_STUN_ATTR_XOR_RELAYED_ADDR          = 0x0016,/**< TURN XOR-RELAYED-ADDRESS  */
    PJ_STUN_ATTR_REQ_ADDR_TYPE             = 0x0017,/**< REQUESTED-ADDRESS-TYPE    */
    PJ_STUN_ATTR_EVEN_PORT                 = 0x0018,/**< TURN EVEN-PORT	    */
    PJ_STUN_ATTR_REQ_TRANSPORT             = 0x0019,/**< TURN REQUESTED-TRANSPORT  */
    PJ_STUN_ATTR_DONT_FRAGMENT             = 0x001A,/**< TURN DONT-FRAGMENT	    */
    PJ_STUN_ATTR_XOR_MAPPED_ADDR           = 0x0020,/**< XOR-MAPPED-ADDRESS	    */
    PJ_STUN_ATTR_TIMER_VAL                 = 0x0021,/**< TIMER-VAL attribute.	    */
    PJ_STUN_ATTR_RESERVATION_TOKEN         = 0x0022,/**< TURN RESERVATION-TOKEN    */
    PJ_STUN_ATTR_XOR_REFLECTED_FROM        = 0x0023,/**< XOR-REFLECTED-FROM	    */
    PJ_STUN_ATTR_PRIORITY                  = 0x0024,/**< PRIORITY		    */
    PJ_STUN_ATTR_USE_CANDIDATE             = 0x0025,/**< USE-CANDIDATE		    */
    PJ_STUN_ATTR_ICMP                      = 0x0030,/**< ICMP (TURN)		    */
    PJ_STUN_ATTR_END_MANDATORY_ATTR,
    PJ_STUN_ATTR_START_EXTENDED_ATTR       = 0x8021,
    PJ_STUN_ATTR_SOFTWARE                  = 0x8022,/**< SOFTWARE attribute.	    */
    PJ_STUN_ATTR_ALTERNATE_SERVER          = 0x8023,/**< ALTERNATE-SERVER.	    */
    PJ_STUN_ATTR_REFRESH_INTERVAL          = 0x8024,/**< REFRESH-INTERVAL.	    */
    PJ_STUN_ATTR_FINGERPRINT               = 0x8028,/**< FINGERPRINT attribute.    */
    PJ_STUN_ATTR_ICE_CONTROLLED            = 0x8029,/**< ICE-CCONTROLLED attribute.*/
    PJ_STUN_ATTR_ICE_CONTROLLING           = 0x802a,/**< ICE-CCONTROLLING attribute*/
    PJ_STUN_ATTR_END_EXTENDED_ATTR
} pj_stun_attr_type;




typedef enum pj_stun_status
{
    PJ_STUN_SC_TRY_ALTERNATE               = 300,  /**< Try Alternate	    */
    PJ_STUN_SC_BAD_REQUEST                 = 400,  /**< Bad Request	    */
    PJ_STUN_SC_UNAUTHORIZED	               = 401,  /**< Unauthorized	    */
    PJ_STUN_SC_FORBIDDEN                   = 403,	/**< Forbidden (TURN)	    */
    PJ_STUN_SC_UNKNOWN_ATTRIBUTE           = 420,  /**< Unknown Attribute	    */
#if 0
    /* These were obsolete in recent rfc3489bis */
    //PJ_STUN_SC_STALE_CREDENTIALS      = 430,  /**< Stale Credentials	    */
    //PJ_STUN_SC_INTEGRITY_CHECK_FAILURE= 431,  /**< Integrity Chk Fail	    */
    //PJ_STUN_SC_MISSING_USERNAME	= 432,  /**< Missing Username	    */
    //PJ_STUN_SC_USE_TLS		= 433,  /**< Use TLS		    */
    //PJ_STUN_SC_MISSING_REALM		= 434,  /**< Missing Realm	    */
    //PJ_STUN_SC_MISSING_NONCE		= 435,  /**< Missing Nonce	    */
    //PJ_STUN_SC_UNKNOWN_USERNAME	= 436,  /**< Unknown Username	    */
#endif
    PJ_STUN_SC_ALLOCATION_MISMATCH      = 437,  /**< TURN Alloc Mismatch    */
    PJ_STUN_SC_STALE_NONCE	        = 438,  /**< Stale Nonce	    */
    PJ_STUN_SC_TRANSITIONING		= 439,  /**< Transitioning.	    */
    PJ_STUN_SC_WRONG_CREDENTIALS	= 441,	/**< TURN Wrong Credentials */
    PJ_STUN_SC_UNSUPP_TRANSPORT_PROTO   = 442,  /**< Unsupported Transport or Protocol (TURN) */
    PJ_STUN_SC_OPER_TCP_ONLY		= 445,  /**< Operation for TCP Only */
    PJ_STUN_SC_CONNECTION_FAILURE       = 446,  /**< Connection Failure	    */
    PJ_STUN_SC_CONNECTION_TIMEOUT       = 447,  /**< Connection Timeout	    */
    PJ_STUN_SC_ALLOCATION_QUOTA_REACHED = 486,  /**< Allocation Quota Reached (TURN) */
    PJ_STUN_SC_ROLE_CONFLICT		= 487,  /**< Role Conflict	    */
    PJ_STUN_SC_SERVER_ERROR	        = 500,  /**< Server Error	    */
    PJ_STUN_SC_INSUFFICIENT_CAPACITY	= 508,  /**< Insufficient Capacity (TURN) */
    PJ_STUN_SC_GLOBAL_FAILURE	        = 600   /**< Global Failure	    */
} pj_stun_status;




typedef struct PACKED {
	uint16_t      type;                              // 2  bytes
	uint16_t      body_length;                       // 2  bytes     - length of data after header
	uint32_t      magic_cookie;                      // 4  bytes     //  21 12 a4 42
	unsigned char transaction_id[12];                // 12 bytes
} stun_message_header_t;



typedef struct PACKED {
	uint16_t  type;
	uint16_t  length;
} stun_attribute_header_t;


typedef struct PACKED {
	char     reserved;
	char     protocol_family;
	uint16_t port;
	uint32_t ip;
} stun_xor_mapped_address_t;


const int HEADER_LENGTH         = sizeof(stun_message_header_t);
const int ATTR_MIN_LENGTH       = 4;
const int TRANSACTION_ID_LENGTH = 12;
//
//
//
//

enum StunMessageType {
	E_MESSAGE_BINDING_REQUEST               = 0x0001,
	E_MESSAGE_BINDING_SUCCESSFULL_RESPONSE  = 0x0101,
	E_MESSAGE_UNKNOWN                       = 0x0000,
};
enum StunAttributeType {
	E_ATTRIBUTE_UNKNOWN                     = 0x0000,
	E_ATTRIBUTE_MAPPED_ADDRESS              = 0x0001, 
	E_ATTRIBUTE_USERNAME                    = 0x0006,
	E_ATTRIBUTE_ICE_CONTROLLED              = 0x802a,
	E_ATTRIBUTE_USE_CANDIDATE               = 0x0025,
	E_ATTRIBUTE_PRIORITY                    = 0x0024,
	E_ATTRIBUTE_MESSAGE_INTEGRITY           = 0x0008,
	E_ATTRIBUTE_FINGERPRINT                 = 0x8028,
	E_ATTRIBUTE_XOR_MAPPED_ADDRESS          = 0x0020,
};






/*
0000   00 01 00 24 21 12 a4 42 69 6c 59 49 52 31 2f 36  ...$!..BilYIR1/6
0010   74 57 2b 33 00 06 00 20 65 42 2f 32 35 73 62 44  tW+3... eB/25sbD
0020   6a 64 6e 65 6c 4b 48 30 49 73 50 67 77 6a 35 33  jdnelKH0IsPgwj53
0030   4c 4c 46 72 76 4d 7a 76                          LLFrvMzv


Message Type: 0x0001 (Binding Request)                  00 01
Message Length: 36                                      00 24
Message Cookie: 2112a442                                21 12 a4 42
Message Transaction ID: 696c594952312f3674572b33        69 6c 59 49 52 31 2f 36 74 57 2b 33
Attributes
 USERNAME: eB/25sbDjdnelKH0IsPgwj53LLFrvMzv
  Attribute Type: USERNAME (0x0006)                     00 06
  Attribute Length: 32                                  00 20
  Username: eB/25sbDjdnelKH0IsPgwj53LLFrvMzv            65 42 2f 32 35 73 62 44 6a 64 6e 65 6c 4b 48 30 49 73 50 67 77 6a 35 33 4c 4c 46 72 76 4d 7a 76
  
*/

#ifdef _WIN32
#pragma pack (pop)
#endif

#endif
