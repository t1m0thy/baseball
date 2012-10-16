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
        br.set_handle_robots(False)
        br.addheaders = [('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT6.0; en-US; rv:1.9.0.6')]
        page = br.open("http://www.pointstreak.com/baseball/boxscore.html?gameid=%s"%gameid)
        
        html = page.read()
        with open(GAME_CACHE_PATH%gameid,'w') as f:
            f.write(html)
        return html
    else:
        return open(GAME_CACHE_PATH%gameid,'r').read()

    
class Event:
    def __init__(self, title, text):
        self.title = title
        self.text = text
        
        
class HalfInning:
    def __init__(self, pbp_string, source="pointstreak"):
        if source=="pointstreak":
            cleaned = [part.strip() for part in pbp_string.split('\t') if len(part.strip()) > 0]
            self.name = cleaned.pop(0)
            self.batting = cleaned.pop(0)
            self.events = []
            while len(cleaned) > 1:
                self.events.append(Event(cleaned.pop(0), cleaned.pop(0)))
            

if __name__ == "__main__":
    import setuplogger
    import logging
    rootlogger = setuplogger.setupRootLogger(logging.INFO)
    rootlogger.info("Test Logging")
    GAME_ID = 110036    

    import gamestate    
    game = gamestate.GameState()
    game.game_id = GAME_ID
    
    html = get_game_html(GAME_ID)
    tree = lxml.html.fromstring(html)    
    innings = [inning for inning in tree.find_class("inning")]
    halfs = [HalfInning(s.text_content()) for s in innings if len(s) > 0] # len > 0 strips unwanted
    
    #===========================================================================
    # General Parser Items
    #===========================================================================

    comma = pp.Literal(',').suppress()
    dash = pp.Literal('-').suppress()
    left_paren = pp.Literal('(').suppress()
    right_paren = pp.Literal(')').suppress()
    period = pp.Literal('.').suppress()

    paranthetical = left_paren + pp.OneOrMore(pp.Word(pp.alphanums+"'")) + right_paren  # single quote in words for "fielder's choice"
    player = (pp.Word(pp.nums).setResultsName("playernum") + pp.Word(pp.alphas).setResultsName("firstname") + pp.Word(pp.alphas).setResultsName("lastname")).setResultsName("player")
    
    #===========================================================================
    # PITCHING    
    #===========================================================================
    pickoff_attempt = (pp.Keyword("Pickoff attempt at") + pp.OneOrMore(pp.Word(pp.alphanums)) + paranthetical).setParseAction(game.add_pickoff)
    swinging = pp.Keyword("Swinging Strike", caseless=True).setParseAction(game.add_swinging_strike)
    called = pp.Keyword("Called Strike", caseless=True).setParseAction(game.add_called_strike)
    ball = pp.Keyword("Ball", caseless=True).setParseAction(game.add_ball)
    foul = pp.Keyword("Foul", caseless=True).setParseAction(game.add_foul)

    #===============================================================================
    #  Outs
    #===============================================================================
    unassisted_out = pp.Word(pp.nums) + pp.Literal('U')
    picked_off = pp.Keyword("PO").setResultsName("pickoff")
    thrown_out = pp.delimitedList(pp.Word(pp.nums), "-") + pp.Optional(picked_off)
    strike_out = pp.Keyword("Strike Out", caseless = True) + pp.Optional(pp.Keyword("swinging"))
    fly_out = pp.Keyword("Fly out to", caseless = True) + pp.OneOrMore(pp.Word(pp.alphas)).setResultsName("field position") 
    out_description = (left_paren + (unassisted_out | thrown_out | strike_out | fly_out) + right_paren).addParseAction(game.out_description) 
    putout = (player + pp.Keyword("putout", caseless=True) + pp.Optional(out_description)).setParseAction(game.add_out) + pp.Keyword("for out number") + pp.Word(pp.nums)
    
    #===============================================================================
    # Base Running
    #===============================================================================

    advances = (player + pp.Keyword("advances to", caseless=True) + pp.OneOrMore(pp.Word(pp.alphanums)).setResultsName("base") + paranthetical.copy().setResultsName("info")).setParseAction(game.add_advance)
        
    #===========================================================================
    # Scoring
    #===========================================================================
    earned = pp.Keyword("Earned", caseless = True) + paranthetical.copy().setResultsName("play")
    unearned = pp.Keyword("Unearned", caseless = True) + paranthetical.copy().setResultsName("player_num")
    scores = (player + pp.Keyword("scores", caseless=True) + (unearned | earned)).setParseAction(game.add_score)

    #===========================================================================
    # SUBS
    #===========================================================================
    position = pp.OneOrMore(pp.Word(pp.alphanums))
    fielder_sub = player.setResultsName("new player") + pp.Keyword("moves to") + position.setResultsName("position") + period
    fielder_sub.setParseAction(game.fielder_substitution)
    offensive_sub = player.setResultsName("new player") + pp.Keyword("subs for") + (pp.Word(pp.alphas).setResultsName("firstname") + pp.Word(pp.alphas).setResultsName("lastname")).setResultsName("replacing") + period
    offensive_sub.setParseAction(game.offensive_substitution)

    #===========================================================================
    # Summary 
    #===========================================================================
    event_parser = pp.delimitedList(fielder_sub | offensive_sub | swinging | called | ball | foul | pickoff_attempt | advances | putout | scores)  + pp.StringEnd()
    
    top = True    
    for h in halfs:
        game.new_half()
        print "%s of inning %s" % (game.get_half_string(), game.inning)
        for e in h.events:
            try:
                event_parser.parseString(e.text)
            except pp.ParseException, pe:
                print e.title
                print "%s of inning %s" % (game.get_half_string(), game.inning)
                print pe.markInputline()
                raise
    
    
    