#!/usr/bin/env python


__author__ = 'esix'


import time

from a3 import messaging
from a3.config import CommandLineConfig, IniConfig, DefaultConfig
from a3.transcoding.gst1.factory import Gst1TranscodingFactory
from a3.logging import LOG
from media_controller import MediaController


media_controller = None


def run():
    global media_controller

    config = CommandLineConfig(IniConfig(DefaultConfig()))
    LOG.info("Config:\n%s", config)

    # TODO: implement configuration-based tanscoding
    transcoding_factory = Gst1TranscodingFactory()

    media_controller = MediaController(config, transcoding_factory)

    messaging.create(config.mq, media_controller).listen()

    #while True:
    #    time.sleep(1)
    #    media_controller.on_timer()


if __name__ == "__main__":
    run()

    while True:
        time.sleep(1)
        #media_controller.on_timer()
