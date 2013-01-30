import os
import logging
logger = logging.getLogger("manager")

import pyparsing as pp
import gamestate
import pointstreakparser as psp
import pointstreakscraper as pss

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import event


def import_game(gameid, cache_path=None):
    gameid = str(gameid)
    scraper = pss.PointStreakScraper(gameid, cache_path)

    game = gamestate.GameState()
    game.home_team_id = scraper.home_team()
    game.visiting_team = scraper.away_team()
    game.game_id = gameid

    #=======================================================================
    # Parse starting lineups and game rosters (any player to appear at all)
    #=======================================================================
    away_starting_lineup, home_starting_lineup = scraper.starting_lineups()
    game.set_away_lineup(away_starting_lineup)
    game.set_home_lineup(home_starting_lineup)

    away_roster, home_roster = scraper.game_rosters()
    game.set_away_roster(away_roster)
    game.set_home_roster(home_roster)

    # pass game to parser
    #TODO: the game wrapper for point streak should be instanced here...
    # it might make sense to just instance a new parser for each game.
    names_in_game = [p.name.replace("_apos;",'\'').replace("&apos;",'\'') for p in away_roster + home_roster]
    parser = psp.PointStreakParser(game, names_in_game)
    
    #=======================================================================
    # Parse plays
    #=======================================================================

    for half in scraper.halfs():
        game.new_half()
        for raw_event in half.raw_events():
            try:
                if not raw_event.is_sub():
                    game.new_batter(raw_event.batter())
                parser.parse_event(raw_event.text())
            except pp.ParseException, pe:
                try:
                    logger.critical("{}: {}\n{}".format(raw_event.title(),
                                                      game.inning_string(),
                                                          pe.markInputline()))
                except:
                    logger.error("possible source: {}".format(raw_event.text()))
                raise
            except:
                try:
                    logger.critical("At {}".format(game.inning_string()))
                except:
                    logger.error("possible source: {}".format(raw_event.text()))
                raise  # StandardError("Error with event: {}".format(raw_event.text()))
    game.set_previous_event_as_game_end()
    return game

def init_database(use_mysql=False, dbname="smallball"):
    """ 
    initialize database 
    if use_mysql is true, use environment variables to set it up
    otherwise default to sqlite
    """
    #engine = create_engine('sqlite:///:memory:', echo=False)
    # "mysql+mysqldb://{user}:{password}@{host}:{port}/{dbname}"
    if use_mysql:
        mysql_setup = "mysql+mysqldb://{user}:{password}@{host}:{port}/{dbname}".format(
                         user="grabber",#os.environ.get('DOTCLOUD_DATA_MYSQL_LOGIN'),
                         password="stitches",#os.environ.get('DOTCLOUD_DATA_MYSQL_PASSWORD'),
                         host=os.environ.get("DOTCLOUD_DATA_MYSQL_HOST"),
                         port=os.environ.get("DOTCLOUD_DATA_MYSQL_PORT"),
                         dbname=dbname
                        )
        engine = create_engine(mysql_setup, echo=False)
    else:
        engine = create_engine('sqlite:///data.sqlite', echo=False)
    event.Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session