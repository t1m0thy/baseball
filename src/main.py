import lxml.html
from lxml.cssselect import CSSSelector
import mechanize
import os
import pyparsing as pp

GAME_CACHE_PATH = "../games/game_%s.html"

def get_game_html(gameid, force_reload=False):      
    if force_reload or not os.path.isfile(GAME_CACHE_PATH%gameid):
        print "getting game "
        br = mechanize.Browser()
        # Browser options
        br.set_handle_equiv(True)
        br.set_handle_redirect(True)
        br.set_handle_referer(True)
        br.set_handle_robots(False)
        br.addheaders = [('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT6.0; en-US; rv:1.9.0.6')]
        page = br.open("http://www.pointstreak.com/baseball/boxscore.html?gameid=%s" % gameid)

        html = br.response().read()
        
        f = open(GAME_CACHE_PATH%gameid,'aw')
        f.write(html)
        f.close()
    return open(GAME_CACHE_PATH%gameid,'r').read()

        
        
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
    rootlogger = setuplogger.setupRootLogger(logging.WARNING)
    rootlogger.info("Test Logging")
    #GAME_ID = 110036   
    #GAME_ID = 109950 
    #GAME_ID = 109678
    #GAME_ID = 109772
    GAME_ID = 109776
    import gamestate    
    game = gamestate.GameState()
    game.game_id = GAME_ID
    
    html = get_game_html(GAME_ID)
    tree = lxml.html.fromstring(html)    
    innings = [inning for inning in tree.find_class("inning")]
    halfs = [HalfInning(s.text_content()) for s in innings if len(s) > 0] # len > 0 strips unwanted
    
    parser = psp.PointStreakParser(game=game)

    top = True    
    for h in halfs:
        game.new_half()
        print "%s of inning %s" % (game.get_half_string(), game.inning)
        for title, text in h.events:
            try:
                parser.parsePlay(text)
            except pp.ParseException, pe:
                #print title
                #print "%s of inning %s" % (game.get_half_string(), game.inning)
                #print pe.markInputline()
                rootlogger.error("%s: %s of inning %s" % (title, game.get_half_string(), game.inning) + '\n' +
                                     pe.markInputline())
                #raise
    
    
    