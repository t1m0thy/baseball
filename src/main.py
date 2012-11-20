import logging
import webbrowser
import pyparsing as pp
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import event
import pointstreakparser as psp
import constants
import gamestate    
import setuplogger


def init_database():
    #engine = create_engine('sqlite:///:memory:', echo=False)
    engine = create_engine('sqlite:///data.sqlite', echo=False)
    event.Base.metadata.create_all(engine) 
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

            

if __name__ == "__main__":
    
    #    testgames = [110036,   
    #                 109950,
    #                 109678,
    #                 109772,
    #                 109776
    #                 ]

    rootlogger = setuplogger.setupRootLogger(logging.WARN)
    logger = logging.getLogger("main")
    playoff = psp.get_game_html(psp.PS_2012_CCL_PLAYOFF_URL, constants.LISTINGS_CACHE_PATH%"PS_CCL_PLAYOFF_2012")

    playoff_soup = BeautifulSoup(playoff)
    links = playoff_soup.find_all("a")
    scores = [l for l in links if l.text == "final"]
    playoff_gameids = [s.attrs["href"].split('=')[1] for s in scores]

    games = []
    parser = psp.PointStreakParser()
    
    session = init_database()

    for gameid in playoff_gameids:
        print gameid        
        try:

            scraper = psp.PointStreakXMLScraper(gameid)
            game = gamestate.GameState()
            game.home_team_id = scraper.home_team()
            game.visiting_team = scraper.away_team()            
            game.game_id = gameid

            parser.set_game(game)
                    
            #=======================================================================
            # Parse Players and Stats
            #=======================================================================
    
            away_starting_lineup, home_starting_lineup = scraper.starting_lineups()
            game.set_away_lineup(away_starting_lineup)
            game.set_home_lineup(home_starting_lineup)
    
            #=======================================================================
            # Parse plays
            #=======================================================================
        
            for half in scraper.halfs():
                game.new_half()
                for raw_event in half.raw_events():                    
                    try:
                        if not raw_event.is_sub():
                            game.new_batter(raw_event.batter())
                        parser.parsePlay(raw_event.text())
                        session.add(game.copy_to_event_model())
                    except pp.ParseException, pe:
                        rootlogger.error("%s: %s of inning %s\n%s" % (raw_event.title(), 
                                                                      game.get_half_string(), 
                                                                      game.inning,
                                                                      pe.markInputline())
                                         )
            session.commit()    
            games.append(game)
        except Exception:
            logger.exception("Error Scraping Game")
            if raw_input("show_problem_page?") == 'y':
                webbrowser.open_new_tab(scraper.review_url())
                raise