import logging
import logging.handlers
import os

def setupRootLogger(level):
    console = logging.StreamHandler()
    console.setLevel(level)
    # set a format which is simpler for console use
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    root = logging.getLogger()
    root.setLevel(level)    
    root.addHandler(console)
    root.setLevel(level)
    return root
