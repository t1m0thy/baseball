import pyparsing as pp


from bs4 import BeautifulSoup

import webbrowser
#get_game_html(PS_2012_CCL_URL, LISTINGS_CACHE_PATH%"PS_CCL_2012")

from constants import POSITIONS

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import event
import pointstreakparser as psp
import constants

def init_database():
    #engine = create_engine('sqlite:///:memory:', echo=False)
    engine = create_engine('sqlite:///data.sqlite', echo=False)
    event.Base.metadata.create_all(engine) 
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

def div_id_dict(element):
    return dict((d.attrs["id"], d) for d in element.findAll("div") if d.has_attr("id"))
      

        
class HalfInning:
    def __init__(self, pbp_string, source="pointstreak"):
        if source=="pointstreak":
            cleaned = [part.strip() for part in pbp_string.split('\t') if len(part.strip()) > 0]
            self.name = cleaned.pop(0)
            self.batting = cleaned.pop(0)
            self.events = []
            while len(cleaned) > 1:
                self.events.append((cleaned.pop(0), cleaned.pop(0)))
            

if __name__ == "__main__":
    import setuplogger
    import logging
    import pointstreakparser as psp
    rootlogger = setuplogger.setupRootLogger(logging.WARN)
    logger = logging.getLogger("main")
#    testgames = [110036,   
#                 109950,
#                 109678,
#                 109772,
#                 109776
#                 ]
    import gamestate    

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
        html = psp.get_pointstreak_game(gameid)
        try:
            soup = BeautifulSoup(html)
            divs = div_id_dict(soup)
    
            tds = divs[psp.DIV_ID_GAME_SUMMARY].findAll("td")
            awayteam, hometeam = [td.text.strip() for td in tds if "psbb_box_score_team" in td.attrs.get("class", [])]
    
            game = gamestate.GameState()
            game.home_team_id = hometeam
            game.visiting_team = awayteam
            
            game.game_id = gameid
            parser.set_game(game)
                    
            #=======================================================================
            # Parse Players and Stats
            #=======================================================================
    
            away_starting_lineup, home_starting_lineup = psp.scrape_pointstreak_xml_lineups(gameid)
    
            #=======================================================================
            # Parse plays
            #=======================================================================
            pbp_div = divs[psp.DIV_ID_PLAYBYPLAY]
            innings = [tr for tr in pbp_div.findAll("tr") if "inning" in tr.attrs.get("class",[])]
            halfs = [HalfInning(s.text) for s in innings]
    
            game.set_away_lineup(away_starting_lineup)
            game.set_home_lineup(home_starting_lineup)
            
            
            for h in halfs:
                game.new_half()
    
                #print "%s of inning %s" % (game.get_half_string(), game.inning)
                for title, text in h.events:
                    try:
                        if "substitution" not in title.lower():
                            game.new_batter(' '.join(title.split()[1:]))
                        game = parser.parsePlay(text)
                        
                        session.add(game.copy_to_event_model())
                    except pp.ParseException, pe:
                        #print title
                        #print "%s of inning %s" % (game.get_half_string(), game.inning)
                        #print pe.markInputline()
                        rootlogger.error("%s: %s of inning %s" % (title, game.get_half_string(), game.inning) + '\n' +
                                             pe.markInputline())
                        #raise
        
            session.commit()    
            games.append(game)
        except Exception:
            logger.exception("Error Scraping Game")
            if raw_input("show_problem_page?") == 'y':
                webbrowser.open_new_tab(psp.get_point_streak_url(gameid))
                raise