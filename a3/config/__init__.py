#!/usr/bin/env python
"""
    Config

    classes for parsing config file, command line arguments and default values

    Command line example:
        # python ./media_controller.py --mq=redis://127.0.0.1/media-controller --profile=192.168.1.250:50000-59999

    Structure of command line
        # python ./media_controller.py --name-1=value-1 --name-2=value-2

    Config file:
        config file name can be specified in command line with key --config=configfile.ini
        if none, then file with name "config.ini" is used

    Structure of config file:
        name=value            # comment

    Example of config file:
        mq=redis://127.0.0.1:6379/media-controller                      # message queue url with self channel name
        profile=192.168.1.2                                             # default profile (ip address is set, port is any)
        profile-external=40000-49999 (0.0.0.0)                          # profile with name "external"
                                                                        #     ip address is not set so mc will try to get machine ip address
                                                                        #     interface is set to 0.0.0.0 (any)
        profile-internal=192.168.1.3:2000-2020,2030                     # interface with name "internal" (ip and port range is given)

    Defaults:
        mq = redis://127.0.0.1/media-controller
        profile = <machine ip>:0
        profile-local=127.0.0.1:0


    mq:
        message queue url with queue name
        <protocol>://<ip:port>/<channel>
        protocol - redis or amqp
        ip:port - location of message queue server
        channel - channel name for media controller to listen

    profile:
        <ip>:<ports> (<interface-ip>)
        profile is ip and port range for rtp connections and ip address to connect

        ip - an IP address of machine which is used by clients (and send in SDP) to access media controller
        ports - ports ranges to open (ranges delimited by comma, values in range
                delimited by minus, default is 0 - any port)
        interface-ip - ip address of interface (default 0.0.0.0 - any)


"""

__author__ = 'RCSLabs'


from ._base import IConfig
from .profile import Profile
from .message_queue_url import MessageQueueUrl

from .command_line_config import CommandLineConfig
from .ini_config import IniConfig
from .default_config import DefaultConfig

if __name__ == "__main__":
    # tests
    pass

