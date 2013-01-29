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
    try:
        game = manager.import_game(gameid)
        for event in game.events():
            session.add(event)
        session.commit()
        games[game.game_id] = game
        jm.complete_job(game.game_id, "pointstreak")
        jm.save()
    except Exception, e:
        raise
        try:
            logger.exception("Error in Game %s in %s of inning %s" % (game.game_id, game.get_half_string(), game.inning))
        except (NameError, AttributeError):
            pass
        try:
            jm.set_job_status(game.game_id, "pointstreak", "error")
            jm.save()
        except NameError:
            pass

if options.game is None:
    jm = JobManager("pending.yml")
    
    for gameid in jm.jobs("pointstreak"):
        process_one(gameid)
else:
    process_one(options.game)

#===============================================================================
# Report Summary
#===============================================================================
print "PARSING COMPLETE"

