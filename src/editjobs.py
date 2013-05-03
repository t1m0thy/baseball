#!/usr/bin/env python
"""
editjobs.py

A command line tool to manage games to parse.  games can be added by
season or individually.  See command line help (-h) for usage instructions.

results will end up in a yaml jobs file.  This yaml file will be read
by grabber.py that also also updates that file to report progress.

#TODO: add some code to easily check jobs have been completed.

"""

import os
import argparse
import logging

import jobmanager
import setuplogger
import pointstreakscraper as pss
from workerconstants import JOBS_PATH, PERSISTENT_FILE_PATH

setuplogger.setupRootLogger(os.environ.get("SB_LOGLEVEL", "warn"))
logger = logging.getLogger("editjobs")

jm = jobmanager.JobManager(JOBS_PATH)
parser = argparse.ArgumentParser("The SBS Job Editor")

parser.add_argument('--addgame', action="store", default=None, help="request to ADD one specific game ID")
parser.add_argument('--delgame', action="store", default=None, help="request to DELETE one specific game ID")
parser.add_argument('--addseason', action="store", default=None, help="request ADD all games IDs in a season")
parser.add_argument('--group', action="store", default="pointstreak", help="game group: ie. pointstreak")
parser.add_argument('--clear', action="store_true", default=False, help="clear all the jobs in the group")
parser.add_argument('--retryfailed', action="store_true", default=False, help="request TODO on any listed games with previous errors")
parser.add_argument('--retrydone', action="store_true", default=False, help="request TODO on all games listed as done")


options = parser.parse_args()
if options.clear:
    jm.clear_jobs(job_group=options.group)
    jm.save()
    print "Cleared {} Job Group".format(options.group)

if options.addgame is not None:
    jm.add_job(options.addgame, job_group=options.group)
    jm.save()
    print "Adding {} game: {}".format(options.group, options.addgame)

if options.delgame is not None:
    jm.add_job(options.delgame, job_group=options.group, job_type=jobmanager.DELETE)
    jm.save()
    print "Deleted {} game: {}".format(options.group, options.delgame)

if options.addseason is not None:
    idlist = pss.scrape_season_gameids(options.addseason, cache_path=PERSISTENT_FILE_PATH)
    jm.add_jobs(idlist, job_group=options.group)
    jm.save()
    print "Added {} season: {}".format(options.group, options.addseason)

if options.retryfailed:
    retry_list = []
    for job in jm.jobs(options.group, do_job_type=jobmanager.ERROR):
        retry_list.append(job)
        jm.set_job(job, options.group, job_type=jobmanager.TODO)
    jm.save()
    print "Will retry {} games: {}".format(options.group, ' '.join(retry_list))

if options.retrydone:
    retry_list = []
    for job in jm.jobs(options.group, do_job_type=jobmanager.DONE):
        retry_list.append(job)
        jm.set_job(job, options.group, job_type=jobmanager.TODO)
    jm.save()
    print "Will retry {} games: {}".format(options.group, ' '.join(retry_list))