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
        intlevel = LOOKUP_LEVEL(level)
    console = logging.StreamHandler()
    console.setLevel(intlevel)
    # set a format which is simpler for console use
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    root = logging.getLogger()
    root.addHandler(console)
    root.setLevel(level)
    return root
