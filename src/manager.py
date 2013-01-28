import logging
logger = logging.getLogger("manager")

import pyparsing as pp
import gamestate
import pointstreakparser as psp
import pointstreakscraper as pss

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import event


def build_game(gameid):
    parser = psp.PointStreakParser()
    # init scraper for this game id
    scraper = pss.PointStreakScraper(gameid)
    # create new game state
    game = gamestate.GameState()
    game.home_team_id = scraper.home_team()
    game.visiting_team = scraper.away_team()
    game.game_id = gameid

    # pass game to parser
    #TODO: the game wrapper for point streak should be instanced here...
    # it might make sense to just instance a new parser for each game.
    parser.set_game(game)

    #=======================================================================
    # Parse starting lineups and game rosters (any player to appear at all)
    #=======================================================================

    away_starting_lineup, home_starting_lineup = scraper.starting_lineups()
    game.set_away_lineup(away_starting_lineup)
    game.set_home_lineup(home_starting_lineup)

    away_roster, home_roster = scraper.game_rosters()
    game.set_away_roster(away_roster)
    game.set_home_roster(home_roster)

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
                logger.critical("%s: %s of inning %s\n%s" % (raw_event.title(),
                                                              game.get_half_string(),
                                                              game.inning,
                                                              pe.markInputline()))
                logger.error("possible source: {}".format(raw_event.text()))
                raise
            except:
                raise  # StandardError("Error with event: {}".format(raw_event.text()))
    game.set_previous_event_as_game_end()
    return game, scraper.review_url()

def init_database():
    """ initialize database """
    #engine = create_engine('sqlite:///:memory:', echo=False)
    engine = create_engine('sqlite:///data.sqlite', echo=False)
    event.Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session