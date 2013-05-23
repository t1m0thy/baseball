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

from models import event
from models import playerinfo
from models import gameinfomodel
from models import teaminfomodel

from constants import BASE_DIR, CONTAINER_PATH
from gamecontainer import GameContainer


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
    try:
        gc = GameContainer(CONTAINER_PATH, gameid)
    except IOError:
        gc = scrape_to_container(gameid, cache_path, session)
    return parse_from_container(gc, game, session)


def scrape_to_container(gameid, cache_path=None, session=None):
    """
    scrape and clean stuff up to save in a GameContainer which is just a shell to hold all needed data for parsing

    the container allows us to have a file that we can manually repair and reparse in the case of scoring errors
    """
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
    #=======================================================================
    # Move into game container
    #=======================================================================

    gc = GameContainer(CONTAINER_PATH, gameid, away, home)

    gc.set_away_lineup(away_starting_lineup)
    gc.set_home_lineup(home_starting_lineup)

    gc.set_away_roster(away_roster)
    gc.set_home_roster(home_roster)

    if hasattr(scraper, "name_spelling_corrections_dict"):
        name_spell_corrections = scraper.name_spelling_corrections_dict()

        def _FS(s):
            for bad, good in name_spell_corrections.items():
                s = re.sub(bad, good, s, flags=re.IGNORECASE)
            s = s.replace("  ", " ").replace("_apos;", '\'').replace("&apos;", '\'')
            s = s.replace("<span class=\"score\">Scores</span>", "Scores")
            s = s.replace("<span class=\"earned\">Earned</span>", "Earned")
            s = s.replace("<span class=\"unearned\">Unearned</span>", "Unearned")
            return s

    else:
        def _FS(s):
            s = s.replace("  ", " ").replace("_apos;", '\'').replace("&apos;", '\'')
            s = s.replace("<span class=\"score\">Scores</span>", "Scores")
            s = s.replace("<span class=\"earned\">Earned</span>", "Earned")
            s = s.replace("<span class=\"unearned\">Unearned</span>", "Unearned")
            return s




    for half in scraper.halfs():
        gc.new_half()
        for raw_event in half.raw_events():
            if raw_event.is_sub():
                gc.add_sub(raw_event.title(), _FS(raw_event.text()))
            else:
                gc.add_event(raw_event.title(), _FS(raw_event.text()), _FS(raw_event.batter()))


    gc.save()
    if scraper.critical_errors:
        raise StandardError("Scraper finished with critical errors.  GameContainer was saved for attempted repairs")
    return gc


def parse_from_container(gc, game=None, session=None):
    ########################################################################

    if game is None:
        game = gamestate.GameState()

    game.home_team_id = gc.home_team
    game.visiting_team = gc.away_team
    game.game_id = gc.gameid

    game.set_away_lineup(gc.away_lineup)
    game.set_home_lineup(gc.home_lineup)

    game.set_away_roster(gc.away_roster)
    game.set_home_roster(gc.home_roster)

    #=======================================================================
    # Parse plays
    #=======================================================================


    # pass game to parser
    #TODO: the game wrapper for point streak should be instanced here...
    # it might make sense to just instance a new parser for each game.
    names_in_game = [p.name for p in gc.away_roster + gc.home_roster]
    parser = psp.PointStreakParser(game, names_in_game)

    for half in gc.halfs():
        game.new_half()
        for event_info in half:
            try:
                if "sub" not in event_info:
                    game.new_batter(event_info["batter"])
                logger.debug("Parsing: {}".format(event_info["text"]))
                parser.parse_event(event_info["text"])
            except pp.ParseException, pe:
                try:
                    logger.critical("{}: {}\n{}".format(event_info["title"],
                                                        game.inning_string(),
                                                        pe.markInputline()))
                except:
                    logger.error("possible source: {}".format(event_info["text"]))
                raise
            except:
                try:
                    logger.critical("At {}".format(game.inning_string()))
                except:
                    logger.error("possible source: {}".format(event_info["text"]))
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
    teaminfomodel.Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
