#!/bin/sh

cd src
tar xvf srtp-1.4.2.tgz
cd srtp
./configure
make
cd ../stun-agent 
make