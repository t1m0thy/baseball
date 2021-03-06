import logging

import setuplogger
import manager
import lineup
from jobmanager import JobManager
import pointstreakscraper as pss

#===============================================================================
# PARSE COMMAND LINE ARGS
#===============================================================================
import argparse
parser = argparse.ArgumentParser("The Small Ball Stats Muncher")
loghelp = """log level: one of 'all', 'debug', 'info', 'warn', 'error', 'critical'.
                Default is 'warn'"""
parser.add_argument('-l', '--log', action="store", default="warn", help=loghelp)
parser.add_argument('-g', '--game', action="store", default=None, help="run one specific game number")
parser.add_argument('-a', '--apply', action="store_true", default=False, help="apply changes to mysql database")

options = parser.parse_args()

#===============================================================================
# SETUP LOGGING
#===============================================================================S

rootlogger = setuplogger.setupRootLogger(options.log)
logger = logging.getLogger("main")

#===========================================================================
# instance parser, setup databse
#===========================================================================
games = {}
session = manager.init_database(use_mysql=options.apply)

# track parsing success game ids


def process_one(gameid):
    print gameid
    game = manager.import_game(gameid, session=session)
    # for event in game.events():
    #     session.add(event)
    # session.commit()
    if game is not None:
        games[game.game_id] = game

if options.game is None:
    jm = JobManager("pending.yml")
    for gameid in jm.jobs("pointstreak"):
        try:
            process_one(gameid)
            jm.complete_job(gameid, "pointstreak")
        except:
            jm.set_job_status(gameid, "pointstreak", "error")
        finally:
            jm.save()
else:
    process_one(options.game)

#===============================================================================
# Report Summary
#===============================================================================

