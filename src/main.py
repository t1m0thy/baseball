import logging
import webbrowser
import yaml
import sys

import commandlineoptions
import setuplogger
import manager
from jobmanager import JobManager

parser = commandlineoptions.parser
options = parser.parse_args()

rootlogger = setuplogger.setupRootLogger(options.log)
logger = logging.getLogger("main")

#===========================================================================
# instance parser, setup databse
#===========================================================================
games = {}
session = manager.init_database(use_mysql=False)

# track parsing success game ids

def process_one(gameid):
    print gameid
    game = manager.import_game(gameid)
    for event in game.events():
        session.add(event)
    session.commit()
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
print "PARSING COMPLETE"

