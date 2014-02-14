CC=g++
CFLAGS=-Wall -O4 -fexpensive-optimizations -funroll-loops
SOURCES=*.cpp gnulib/*.c
LIB_SRTP=../srtp
EXECUTABLE=../../stun-agent
INCLUDES=-I$(LIB_SRTP)/include -I$(LIB_SRTP)/crypto/include
LIBS=-L. -L$(LIB_SRTP)

all: 
	$(CC) $(CFLAGS) $(INCLUDES) $(LIBS) -DHAVE_CONFIG_H $(SOURCES) $(LIB_SRTP)/libsrtp.a -lsrtp -lpthread -o $(EXECUTABLE)


clean:
	rm -rf *.o
