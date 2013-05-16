import os

import logging
logger = logging.getLogger("manager")

import pyparsing as pp
import gamestate
import gameinfo

import pointstreakparser as psp
import pointstreakscraper as pss
from models.playerinfo import PlayerInfo


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import event
from models import playerinfo
from models import gameinfomodel

CHECKED_PLAYERS = {}


def find_new_player_id(session, base_name):
    index = 1
    while index < 10:
        new_id = base_name + "{:03d}".format(index)
        player_models = session.query(PlayerInfo).filter_by(SBS_ID=new_id)
        if player_models.count() == 0:
            return new_id
        index += 1
    raise StandardError("Could not find a unqiue id for base name {}".format(base_name))


def import_game(gameid, cache_path=None, game=None, session=None):
    gameid = str(gameid)

    scraper = pss.PointStreakScraper(gameid, cache_path)

    game_info = gameinfo.GameInfo(gameid)
    game_info.set_game_info(scraper.game_info)

    #=======================================================================
    # Parse starting lineups and game rosters (any player to appear at all)
    #=======================================================================

    # pass in starting lineups so the rosters include those player objects
    away_roster, home_roster = scraper.game_rosters()
    away_starting_lineup, home_starting_lineup = scraper.starting_lineups(away_roster, home_roster)
    game_info.set_starting_players(away_starting_lineup, home_starting_lineup)

    # sync up with the player database.
    if session is not None:
        for player in away_roster + home_roster:
            logger.info("Checking DB for Player {}".format(player.name))
            try:
                cached = (player.name.first(), player.name.last(), player.team_id) in CHECKED_PLAYERS
            except TypeError:
                logger.warning("Could not cache {}".format((player.name.first(), player.name.last(), player.team_id)))
                cached = False
            if cached:
                player.name.set_id(CHECKED_PLAYERS[(player.name.first(), player.name.last(), player.team_id)])
            else:
                player_models = session.query(PlayerInfo).filter_by(FIRST_NAME=player.name.first(), LAST_NAME=player.name.last(), TEAM_ID=player.team_id)
                if player_models.count() < 1:
                    sbs_id = find_new_player_id(session, player.name.id())
                    player.name.set_id(sbs_id)
                    session.add(player.to_model())
                    logger.info("Add {} to DB".format(player.name))
                elif player_models.count() > 1:
                    logger.warning("More than one player found for name: {} {}".format(player.name.first(), player.name.last()))
                    player.name.set_id(player_models[0].SBS_ID)
                elif player_models.count() == 1:
                    player.name.set_id(player_models[0].SBS_ID)
                    #m = player.to_model(player_models[0])  # update existing model
                    #session.merge(m)
                CHECKED_PLAYERS[(player.name.first(), player.name.last(), player.team_id)] = player.name.id()

        game_info_query = session.query(gameinfomodel.GameInfoModel).filter_by(GAME_ID=gameid)
        if game_info_query.count() < 1:
            session.add(game_info.as_model())
            logger.info("added game info to db")
        elif game_info_query.count() > 1:
            logger.warning("More than one game found with id: {}".format(game.game_id))

    if game is None:
        game = gamestate.GameState()
    home = scraper.home_team()
    away = scraper.away_team()

    game.home_team_id = home
    game.visiting_team = away
    game.game_id = gameid

    game.set_away_lineup(away_starting_lineup)
    game.set_home_lineup(home_starting_lineup)

    game.set_away_roster(away_roster)
    game.set_home_roster(home_roster)

    #=======================================================================
    # Parse plays
    #=======================================================================

    # pass game to parser
    #TODO: the game wrapper for point streak should be instanced here...
    # it might make sense to just instance a new parser for each game.
    names_in_game = [p.name.replace("_apos;", '\'').replace("&apos;", '\'') for p in away_roster + home_roster]
    parser = psp.PointStreakParser(game, names_in_game)

    for half in scraper.halfs():
        game.new_half()
        for raw_event in half.raw_events():
            try:
                if not raw_event.is_sub():
                    game.new_batter(raw_event.batter())
                logger.debug("Parsing: {}".format(raw_event.text()))
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

    for p in game.home_roster + game.away_roster:
        for stat in ["AB", "R", "H", "RBI", "BB", "SO"]:
            if p.bat_stats.get(stat, 0) != p.verify_bat_stats.get(stat, 0):
                logger.error(" counted {} {} does not equal reported {} {} for player {}".format(stat, p.bat_stats.get(stat, 0), stat, p.verify_bat_stats.get(stat, 0), p.name))

    if session is not None:
        for e in game.events():
            session.add(e)
        session.commit()
    return game


def init_database(use_mysql=False, dbname="sbs"):
    """
    initialize database
    if use_mysql is true, use environment variables to set it up
    otherwise default to sqlite
    """
    #engine = create_engine('sqlite:///:memory:', echo=False)
    # "mysql+mysqldb://{user}:{password}@{host}:{port}/{dbname}"
    if use_mysql:
        db_setup = dict(user=os.environ.get('MYSQL_LOGIN'),
                        password=os.environ.get('MYSQL_PASSWORD'),
                        host="127.0.0.1",
                        port=os.environ.get('MYSQL_PORT', 3006),
                        dbname=dbname
                        )
        mysql_setup = "mysql+mysqldb://{user}:{password}@{host}:{port}/{dbname}".format(**db_setup)
        engine = create_engine(mysql_setup, echo=False)
    else:
        engine = create_engine('sqlite:///data.sqlite', echo=False)
    event.Base.metadata.create_all(engine)
    gameinfomodel.Base.metadata.create_all(engine)
    playerinfo.Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
