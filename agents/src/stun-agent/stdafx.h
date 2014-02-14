// stdafx.h : include file for standard system include files,
// or project specific include files that are used frequently, but
// are changed infrequently
//

#ifndef __STDAFX_H__
#define __STDAFX_H__

#ifndef _WIN32_WINNT            // Specifies that the minimum required platform is Windows Vista.
#define _WIN32_WINNT 0x0600     // Change this to the appropriate value to target other versions of Windows.
#endif


#include <stdio.h>
#include <sys/types.h>
#include <string.h>
#include <stdlib.h>
#include <cstdlib>
#include <time.h>


#include <string>
#include <list>
#include <map>
#include <vector>
#include <exception>
#include <sstream>
#include <iostream>
#include <iomanip>



#ifdef _WIN32
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include "stdint.h"
#include <tchar.h>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <iphlpapi.h>
#include <process.h>
#define THREAD_FUNC DWORD WINAPI


typedef int       socklen_t;
typedef HANDLE    pthread_t;
typedef uint16_t  ssize_t;

#else

#include <stdint.h>
#include <unistd.h> 
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/un.h>
#include <pthread.h>

#define THREAD_FUNC void*
#endif


#endif //__STDAFX_H__
