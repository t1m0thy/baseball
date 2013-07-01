import os
import re
import logging
logger = logging.getLogger("manager")

import pyparsing as pp
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import gamestate
import gameinfo
import pointstreakparser as psp
import pointstreakscraper as pss
from models.playerinfo import PlayerInfo
import subtracker

from models import event
from models import playerinfo
from models import gameinfomodel
from models import teaminfomodel
import gamewrapper

from constants import BASE_DIR, CONTAINER_PATH
from gamecontainer import GameContainer, GameContainerLogHandler

from setuplogger import GameContextFilter

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


def import_game(gameid, cache_path=None, game=None, session=None, force_fresh=False):
    try:
        if force_fresh:
            raise IOError("Not actually an IOError.")
        gc = GameContainer(CONTAINER_PATH, gameid)
    except IOError:
        gc = scrape_to_container(gameid, cache_path, session)
    return parse_from_container(gc, game, session)


def setup_scraper(gameid, cache_path=None, session=None):
    gameid = str(gameid)

    scraper = pss.PointStreakScraper(gameid, cache_path)

    #=======================================================================
    # Parse Teams and check DB
    #=======================================================================

    home = scraper.home_team()
    away = scraper.away_team()

    if session:
        for team_name in (home, away):
            session.query(teaminfomodel.TeamInfo).filter_by(FULL_NAME=team_name)

    game_info = gameinfo.GameInfo(gameid)
    game_info.set_game_info(scraper.game_info)

    #=======================================================================
    # Parse starting lineups and game rosters (any player to appear at all)
    #=======================================================================

    # pass in starting lineups so the rosters include those player objects
    #away_roster, home_roster = scraper.game_rosters()
    away_starting_lineup, home_starting_lineup, away_roster, home_roster = scraper.starting_lineups()
    game_info.set_starting_players(away_starting_lineup, home_starting_lineup)


    # sync up with the player database.
    if session is not None:
        game_info_query = session.query(gameinfomodel.GameInfoModel).filter_by(GAME_ID=gameid)

        if game_info_query.count() < 1:
            session.add(game_info.as_model())
            logger.info("added game info to db")
        else:
            if game_info_query.count() > 1:
                logger.warning("More than one game found with id: {}".format(gameid))
            game_info_query.delete()
            session.add(game_info.as_model())

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
        session.commit()
    return scraper, away_starting_lineup, home_starting_lineup, away_roster, home_roster

def scrape_to_container(gameid, cache_path=None, session=None, save_container=True):
    """
    scrape and clean stuff up to save in a GameContainer which is just a shell to hold all needed data for parsing

    the container allows us to have a file that we can manually repair and reparse in the case of scoring errors
    """

    d = setup_scraper(gameid, cache_path, session)
    scraper, away_starting_lineup, home_starting_lineup, away_roster, home_roster = d
    #=======================================================================
    # Move into game container
    #=======================================================================

    home = scraper.home_team()
    away = scraper.away_team()

    gc = GameContainer(CONTAINER_PATH, gameid, away, home)

    gc.url = pss.make_html_url(gameid)

    gc.set_away_roster(away_roster)
    gc.set_home_roster(home_roster)

    for half in scraper.halfs():
        gc.new_half()
        for raw_event in half.raw_events():
            if raw_event.is_sub():
                gc.add_sub(raw_event.title(), raw_event.text())
            else:
                gc.add_event(raw_event.title(), raw_event.text(), raw_event.batter(), raw_event.batter_number())


    if save_container:
        gc.save()
    if scraper.critical_errors:
        raise StandardError("Scraper finished with critical errors.  GameContainer was saved for attempted repairs")
    return gc


def parse_from_container(gc, game=None, session=None):
    names_in_game = [p.name for p in gc.away_roster() + gc.home_roster()]
    home_subs = []
    away_subs = []
    home_batting = False
    for half in gc.halfs():
        for event_info in half:
            if "batter" not in event_info:
                text = event_info["text"]
                if text.startswith("Offsensive"):
                    if home_batting:
                        home_subs.append(text)
                    else:
                        away_subs.append(text)
                else:
                    if home_batting:
                        away_subs.append(text)
                    else:
                        home_subs.append(text)
        home_batting = not home_batting

    for sublist, lineup in ((home_subs, gc.home_lineup()), (away_subs, gc.away_lineup())):
        st = subtracker.SubTracker(lineup)
        subparser = psp.PointStreakParser(st, names_in_game)
        for sub in sublist:
            try:
                subparser.parse_event(sub)
            except Exception, e:
                logger.critical("Problem parsing sub from: {}.  {}".format(sub, str(e)))
        for player in lineup:
            if len(player.starting_position) != 1:
                logger.error("Error determining positions for {}.  starting position list {}".format(player.name, player.starting_position))
            else:
                player.set_position(player.starting_position[0])


    if game is None:
        game = gamestate.GameState()

    # setup log filter to add contextual info to logs
    game_context_log_filter = GameContextFilter()
    logger.addFilter(game_context_log_filter)
    game.logger.addFilter(game_context_log_filter)  # will add context (current inning etc) to the error logs
    psp.gamewrapper.logger.addFilter(game_context_log_filter)

    gc_handler = GameContainerLogHandler(gc)
    game.logger.addHandler(gc_handler)  # will ensure that errors get inserted into container
    logger.addHandler(gc_handler)
    psp.gamewrapper.logger.addHandler(gc_handler)
    try:
        game.home_team_id = gc.home_team
        game.visiting_team = gc.away_team
        game.game_id = gc.gameid

        game.set_away_lineup(gc.away_lineup())
        game.set_home_lineup(gc.home_lineup())

        game.set_away_roster(gc.away_roster())
        game.set_home_roster(gc.home_roster())

        #=======================================================================
        # Parse plays
        #=======================================================================

        gw = gamewrapper.GameWrapper(game)
        parser = psp.PointStreakParser(gw, names_in_game)

        for half in gc.halfs():
            game.new_half()
            game_context_log_filter.inning = game.inning
            game_context_log_filter.is_bottom = bool(game.half_inning)
            game_context_log_filter.event_num = 0
            for event_info in half:
                try:
                    if "batter" in event_info:
                        game.new_batter(event_info["batter"], event_info.get("batter_number"))
                    logger.debug("Parsing: {}".format(event_info["text"]))
                    parser.parse_event(event_info["text"])
                except pp.ParseException, pe:
                    try:
                        logger.critical("PARSE ERROR - " + pe.markInputline(),
                                        extra=dict(title=event_info["title"],
                                                    inning=game.inning,
                                                    bottom=game.half_inning
                                                    )
                                        )
                    except:
                        logger.error("Error logging error! Possible source: {}".format(event_info["text"]))
                    raise
                except Exception, e:
                    try:
                        logger.critical(str(e))
                    except:
                        logger.error("Error loggin error!  Possible source: {}".format(event_info["text"]))
                    raise  # StandardError("Error with event: {}".format(raw_event.text()))
                game_context_log_filter.event_num += 1

        game.set_previous_event_as_game_end()

        for p in game.home_roster + game.away_roster:
            for stat in ["AB", "R", "H", "RBI", "BB", "SO"]:
                if p.bat_stats.get(stat, 0) != p.verify_bat_stats.get(stat, 0):
                    logger.warning(" counted {} {} does not equal reported {} {} for player {}".format(stat, p.bat_stats.get(stat, 0), stat, p.verify_bat_stats.get(stat, 0), p.name))

        if session is not None:
            for e in game.events():
                session.add(e)
            session.commit()
    finally:
        gc.save()
        game.logger.removeFilter(game_context_log_filter)
        game.logger.removeHandler(gc_handler)
        logger.removeFilter(game_context_log_filter)
        logger.removeHandler(gc_handler)
        psp.gamewrapper.logger.removeFilter(game_context_log_filter)
        psp.gamewrapper.logger.removeHandler(gc_handler)


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
    teaminfomodel.Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
