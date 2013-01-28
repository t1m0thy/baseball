import argparse

parser = argparse.ArgumentParser("The Small Ball Stats Muncher")
loghelp = """log level: one of 'all', 'debug', 'info', 'warn', 'error', 'critical'.  
                Default is 'warn'"""
parser.add_argument('-l', '--log', action="store", default="warn", help=loghelp)
