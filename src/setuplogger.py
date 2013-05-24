import logging

LOOKUP_LEVEL = {"all": 0,
                "debug": logging.DEBUG,
                "info": logging.INFO,
                "warn": logging.WARN,
                "warning": logging.WARNING,
                "error": logging.ERROR,
                "critical": logging.CRITICAL,
                "fatal": logging.FATAL
                }

def setupRootLogger(level):
    try:
        intlevel = int(level)
    except ValueError:
        intlevel = LOOKUP_LEVEL[level]
    console = logging.StreamHandler()
    console.setLevel(intlevel)
    # set a format which is simpler for console use
    formatter = logging.Formatter(" %(levelname)8s - %(asctime)s - %(name)s -%(message)s")
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    root = logging.getLogger()
    root.addHandler(console)
    root.setLevel(intlevel)
    return root


class GameContextFilter(logging.Filter):
    """
    This is a filter which injects contextual information into the log.

    """

    def __init__(self):
        logging.Filter.__init__(self)
        self.inning = 0
        self.is_bottom = 0
        self.event_num = 0

    def filter(self, record):
        record.inning = self.inning
        record.is_bottom = self.is_bottom
        record.event_num = self.event_num
        return True
