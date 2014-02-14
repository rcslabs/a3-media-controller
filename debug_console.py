"""Debug console



"""
from a3 import messaging
from a3.messaging import IMqListener


class DebugConsole(IMqListener):

    def __init__(self, config):
        self.config = config
        self.mc_channel = None
        print "Commands:"
        print "    connect <MC id> - connect to media controller instance"




if __name__ == "__main__":
    #
    # test part for app
    #
    from config import IniConfig
    
    config = IniConfig(None, section="debug console")

    mq_url = config.get_mq()
    if "%" in mq_url:
        # replace % with random number
        pass
    print "mq_url =", mq_url


    app = DebugConsole({})
    mq = messaging.ParserMq(messaging.Mq(mq_url))
    mq.set_listener(app)
    mq.start();

