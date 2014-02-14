#!/usr/bin/env python


import threading
from subprocess import Popen, PIPE
import re
from abc import ABCMeta, abstractmethod


class Agent(threading.Thread):
    __metaclass__ = ABCMeta

    def __init__(self, command, name=""):
        threading.Thread.__init__(self)
        self.name = name
        print "Execute command:", command
        self.pipe = Popen(command, stdout=PIPE, stdin=PIPE)

    def run(self):
        while True:
            line = self.pipe.stdout.readline()
            if not line:
                break

            g = re.findall(r"(\w+)=(\S+)", line)
            #print "RECEIVED FROM", self.name, ":", g
            msg = {}
            for pair in g:
                name = pair[0]
                value = pair[1]
                msg[name] = value

            if "type" in msg:
                self.on_message(msg, None)

        print self.name, " closed"

    def send_message(self, message):
        s = []
        for k, v in message.iteritems():
            if v is not None:
                s.append(k + "=" + str(v))
        try:
            str_message = " ".join(s)
            print "Msg to", self.name,":", str_message
            self.send_message_str(str_message)
        except:
            pass

    def send_message_str(self, str_message):
        self.pipe.stdin.write(str_message + "\n")

    @abstractmethod
    def on_message(self, msg, mq):
        """
        message received
        """

    def stop(self):
        print "trying to stop agent ", self.name
        self.pipe.stdout.close()
        self.pipe.stdin.close()
