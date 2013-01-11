import logging
import webbrowser
import pyparsing as pp
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import event
import pointstreakparser as psp
import pointstreakscraper as pss
import gamestate    
import setuplogger
import scrapetools


def init_database():
    """ initialize database """
    #engine = create_engine('sqlite:///:memory:', echo=False)
    engine = create_engine('sqlite:///data.sqlite', echo=False)
    event.Base.metadata.create_all(engine) 
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

            

if __name__ == "__main__":
    rootlogger = setuplogger.setupRootLogger(logging.WARN)
    logger = logging.getLogger("main")

    #===============================================================================
    # temporary code to grab all the CCL playoff game ids 
    #===============================================================================
    playoff = scrapetools.get_cached_url(pss.PS_2012_CCL_PLAYOFF_URL, pss.LISTINGS_CACHE_PATH%"PS_CCL_PLAYOFF_2012")
    playoff_soup = BeautifulSoup(playoff)
    links = playoff_soup.find_all("a")
    scores = [l for l in links if l.text == "final"]
    playoff_gameids = [s.attrs["href"].split('=')[1] for s in scores]
    
    
    #===========================================================================
    # instance parser, setup databse
    #===========================================================================
    games = []    
    parser = psp.PointStreakParser()    
    session = init_database()

    # track parsing success game ids   
    success_games = []
    failed_games = []

    for gameid in playoff_gameids:
        print gameid        
        try:
            # init scraper for this game id
            scraper = pss.PointStreakXMLScraper(gameid)
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
                        raise
                    except:
                        raise# StandardError("Error with event: {}".format(raw_event.text()))
            game.set_previous_event_as_game_end()
            
            for event in game.events():
                session.add(event)
            session.commit()
            games.append(game)
            success_games.append(game.game_id)
        except Exception, e:
            logger.exception("Error in Game %s in %s of inning %s" % (game.game_id, game.get_half_string(), game.inning))
            logger.error("possible source: {}".format(raw_event.text()))
            failed_games.append(game.game_id)
            if raw_input("show_problem_page?") == 'y':
                webbrowser.open_new_tab(scraper.review_url())
            raise

    #===============================================================================
    # Report Summary
    #===============================================================================
    print "PARSING COMPLETE"
    print "Success count: {}".format(len(success_games))
    print "Fail count: {}".format(len(failed_games))