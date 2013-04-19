#!/usr/bin/env python

import os
import sys
import time
import signal
import logging

# this allows us to keep all the library code in the smallball directory
# I am doing this instead of refering to the package because it makes
# refering to smallball project easier in my code tree
sys.path.append("/home/dotcloud/current/smallball")

import manager
import jobmanager 
import setuplogger
from models.event import Event
from workerconstants import PERSISTENT_FILE_PATH, JOBS_PATH

setuplogger.setupRootLogger(os.environ.get("SB_LOGLEVEL", "warn"))
logger = logging.getLogger("main")

# this is a hack to get dotcloud print outpout into logs
sys.stdout = sys.stderr


def delete_game(session, gameid):
    events = session.query(Event).filter(Event.GAME_ID==gameid)
    count = events.count()
    if count > 0:
        events.delete()
    session.commit()
    print ">>>> deleted {} entries with id {}".format(count, gameid)
    
def main():
    f = open(os.path.join(PERSISTENT_FILE_PATH, "test.txt"), 'a')
    f.write("opened file at {}\n".format(time.asctime()))
    f.close()
            
    session = manager.init_database(use_mysql=True)
    
    while True:
        if os.path.isfile(JOBS_PATH):
            jm = jobmanager.JobManager(JOBS_PATH)
            for group in jm.groups():
                
                for gameid in jm.jobs(group, do_job_type=jobmanager.DELETE):
                    delete_game(session, gameid)
                    jm.complete_job(gameid, group)
                    jm.save()
                for gameid in jm.jobs(group, do_job_type=jobmanager.TODO):
                    try:
                        delete_game(session, gameid)
                        session.query(Event).filter(Event.GAME_ID==gameid).delete()
                        print ">>>> processing {}".format(gameid)
                        game = manager.import_game(gameid, PERSISTENT_FILE_PATH)
                        for event in game.events():
                            session.add(event)
                        session.commit()
                        jm.complete_job(gameid, group)
                        jm.save()
                        print ">>>> GAME {} complete. {} remaining in this set".format(gameid, jm.job_count())
                    except Exception:
                        logger.exception("Error while processing {} game {}".format(group, gameid))
                        jm.set_job(gameid, group, jobmanager.ERROR)
                        jm.save()
                print "jobs complete in group " + group
            print "no jobs remaining"

        else:
            print "no jobs file found, waiting to find it"
        jobs__last_editted = os.stat(JOBS_PATH).st_mtime
        tries = 0
        while jobs__last_editted == os.stat(JOBS_PATH).st_mtime:
            time.sleep(5)
            tries ++ 1
            if tries == 12:
                tries = 0
                print "waiting for changes to {}".format(JOBS_PATH)

                
# Callback called when you run `supervisorctl stop'
def sigterm_handler(signum, frame):
    sys.stderr.write("Terminated at {}\n".format(time.asctime()))
    sys.exit(0)

# Bind our callback to the SIGTERM signal and run the daemon:
signal.signal(signal.SIGTERM, sigterm_handler)
main()
